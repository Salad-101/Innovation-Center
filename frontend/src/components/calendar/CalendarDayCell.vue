<script setup>
import { useIdeasStore } from "../../stores/ideas"
import { getIdeaColor } from "../../utils/formatters"

const MAX_VISIBLE = 3

defineProps({
    day: { type: Number, required: true },
    inCurrentMonth: { type: Boolean, default: true },
    isToday: { type: Boolean, default: false },
    isPast: { type: Boolean, default: false },
    isSelected: { type: Boolean, default: false },
    meetings: { type: Array, default: () => [] },
})

const emit = defineEmits(["select", "select-meeting"])

const store = useIdeasStore()

function ideaTitle(meeting) {
    return store.getIdea(meeting.idea)?.title || "Unknown idea"
}
</script>

<template>
    <button
        type="button"
        @click="emit('select')"
        :class="[
            inCurrentMonth ? '' : 'opacity-40',
            isSelected
                ? 'border-indigo-500 ring-1 ring-indigo-500'
                : 'border-slate-200 dark:border-white/[0.06]',
        ]"
        class="flex h-24 flex-col items-stretch gap-1 overflow-hidden rounded-xl border bg-white p-1.5 text-left transition hover:border-indigo-300 dark:bg-[#15181f] dark:hover:border-indigo-500/40 sm:h-28"
    >
        <span
            :class="isToday
                ? 'bg-indigo-500 text-white'
                : 'text-slate-500 dark:text-slate-400'"
            class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[10px] font-semibold"
        >
            {{ day }}
        </span>

        <div class="min-h-0 flex-1 space-y-1 overflow-hidden">
            <div
                v-for="meeting in meetings.slice(0, MAX_VISIBLE)"
                :key="meeting.id"
                @click.stop="emit('select-meeting', meeting)"
                :class="[getIdeaColor(meeting.idea), isPast ? 'opacity-50' : '']"
                class="truncate rounded px-1.5 py-0.5 text-[9px] font-medium text-white"
                :title="ideaTitle(meeting)"
            >
                {{ ideaTitle(meeting) }}
            </div>

            <p v-if="meetings.length > MAX_VISIBLE" class="text-[9px] text-slate-400">
                +{{ meetings.length - MAX_VISIBLE }} more
            </p>
        </div>
    </button>
</template>
