<script setup>
import { computed, ref } from "vue"
import { useIdeasStore } from "../../stores/ideas"
import { getLocalToday } from "../../utils/formatters"
import CalendarDayCell from "./CalendarDayCell.vue"
import SelectedDayMeetings from "./SelectedDayMeetings.vue"

const emit = defineEmits(["edit-meeting", "schedule-meeting", "delete-meeting"])

const store = useIdeasStore()

const WEEKDAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

const today = getLocalToday()
const [todayYear, todayMonthNum] = today.split("-").map(Number)

const viewDate = ref(new Date(todayYear, todayMonthNum - 1, 1))
const selectedDateKey = ref(today)

const monthLabel = computed(() =>
    new Intl.DateTimeFormat("en", { month: "long", year: "numeric" }).format(viewDate.value)
)

function toDateKey(date) {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, "0")
    const day = String(date.getDate()).padStart(2, "0")
    return `${year}-${month}-${day}`
}

// All meetings, across every idea, grouped by date so each grid cell is a
// cheap lookup instead of filtering the full list per day.
const meetingsByDate = computed(() => {
    const map = {}

    for (const meeting of store.meetings) {
        if (!map[meeting.date]) {
            map[meeting.date] = []
        }
        map[meeting.date].push(meeting)
    }

    for (const key in map) {
        map[key].sort((a, b) => a.time.localeCompare(b.time))
    }

    return map
})

// 6 weeks x 7 days, including the leading/trailing days from adjacent
// months needed to fill the grid.
const days = computed(() => {
    const year = viewDate.value.getFullYear()
    const month = viewDate.value.getMonth()

    const firstOfMonth = new Date(year, month, 1)
    const gridStart = new Date(year, month, 1 - firstOfMonth.getDay())

    const cells = []

    for (let i = 0; i < 42; i++) {
        const cellDate = new Date(gridStart.getFullYear(), gridStart.getMonth(), gridStart.getDate() + i)
        const key = toDateKey(cellDate)

        cells.push({
            key,
            day: cellDate.getDate(),
            inCurrentMonth: cellDate.getMonth() === month,
            isToday: key === today,
            isPast: key < today,
            meetings: meetingsByDate.value[key] || [],
        })
    }

    return cells
})

const selectedDayMeetings = computed(() =>
    meetingsByDate.value[selectedDateKey.value] || []
)

function prevMonth() {
    viewDate.value = new Date(viewDate.value.getFullYear(), viewDate.value.getMonth() - 1, 1)
}

function nextMonth() {
    viewDate.value = new Date(viewDate.value.getFullYear(), viewDate.value.getMonth() + 1, 1)
}

function goToToday() {
    viewDate.value = new Date(todayYear, todayMonthNum - 1, 1)
    selectedDateKey.value = today
}

function selectDay(cell) {
    selectedDateKey.value = cell.key
}
</script>

<template>
    <div class="min-h-0 flex-1 overflow-auto p-6">
        <div class="mx-auto max-w-5xl">

            <div class="mb-6 flex flex-wrap items-center justify-between gap-3">
                <div>
                    <h2 class="text-lg font-semibold">Calendar</h2>
                    <p class="mt-1 text-xs text-slate-400">Every idea's upcoming meetings, by date.</p>
                </div>

                <div class="flex items-center gap-2">
                    <button @click="goToToday" class="rounded-xl border border-slate-200 px-3 py-2 text-xs dark:border-white/[0.08]">Today</button>
                    <button @click="prevMonth" class="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 text-sm dark:border-white/[0.08]">‹</button>
                    <span class="w-32 text-center text-xs font-medium">{{ monthLabel }}</span>
                    <button @click="nextMonth" class="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 text-sm dark:border-white/[0.08]">›</button>
                </div>
            </div>

            <div class="mb-1.5 grid grid-cols-7 gap-1.5 text-center text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                <span v-for="label in WEEKDAY_LABELS" :key="label">{{ label }}</span>
            </div>

            <div class="mb-6 grid grid-cols-7 gap-1.5">
                <CalendarDayCell
                    v-for="cell in days"
                    :key="cell.key"
                    :day="cell.day"
                    :in-current-month="cell.inCurrentMonth"
                    :is-today="cell.isToday"
                    :is-past="cell.isPast"
                    :is-selected="cell.key === selectedDateKey"
                    :meetings="cell.meetings"
                    @select="selectDay(cell)"
                    @select-meeting="meeting => emit('edit-meeting', meeting)"
                />
            </div>

            <SelectedDayMeetings
                :date-key="selectedDateKey"
                :meetings="selectedDayMeetings"
                @schedule="emit('schedule-meeting', null, selectedDateKey)"
                @edit-meeting="meeting => emit('edit-meeting', meeting)"
                @delete-meeting="meeting => emit('delete-meeting', meeting)"
            />

        </div>
    </div>
</template>
