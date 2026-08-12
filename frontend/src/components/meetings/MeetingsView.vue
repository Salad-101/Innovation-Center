<script setup>
import { computed, ref } from "vue"
import { useIdeasStore } from "../../stores/ideas"
import { getLocalToday } from "../../utils/formatters"
import UpcomingMeetingCard from "./UpcomingMeetingCard.vue"
import PastMeetingRow from "./PastMeetingRow.vue"

const emit = defineEmits(["edit-meeting", "delete-meeting"])

const store = useIdeasStore()

const meetingSearch = ref("")

const filteredMeetings = computed(() => {
    if (!meetingSearch.value.trim()) {
        return store.meetings
    }

    const query = meetingSearch.value.trim().toLowerCase()

    return store.meetings.filter(meeting => {
        const idea = store.getIdea(meeting.idea)

        return (
            idea?.title?.toLowerCase().includes(query) ||
            meeting.location?.toLowerCase().includes(query) ||
            meeting.notes?.toLowerCase().includes(query)
        )
    })
})

const upcomingMeetings = computed(() => {
    const today = getLocalToday()

    return filteredMeetings.value
        .filter(meeting => meeting.date >= today)
        .sort((a, b) => `${a.date} ${a.time}`.localeCompare(`${b.date} ${b.time}`))
})

const pastMeetings = computed(() => {
    const today = getLocalToday()

    return filteredMeetings.value
        .filter(meeting => meeting.date < today)
        .sort((a, b) => `${b.date} ${b.time}`.localeCompare(`${a.date} ${a.time}`))
})
</script>

<template>
    <div class="min-h-0 flex-1 overflow-auto p-6">
        <div class="mx-auto max-w-5xl">

            <div class="mb-6 flex items-center justify-between">
                <div>
                    <h2 class="text-lg font-semibold">Meetings</h2>
                    <p class="mt-1 text-xs text-slate-400">Schedule and manage mentor meetings.</p>
                </div>

                <input
                    v-model="meetingSearch"
                    type="text"
                    placeholder="Search meetings..."
                    class="h-9 w-56 rounded-xl border border-slate-200 bg-white px-3 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
                />
            </div>

            <section>
                <h3 class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Upcoming</h3>

                <div v-if="upcomingMeetings.length === 0" class="rounded-2xl border border-dashed border-slate-200 p-10 text-center dark:border-white/[0.07]">
                    <p class="text-xs text-slate-400">No upcoming meetings.</p>
                </div>

                <div class="space-y-3">
                    <UpcomingMeetingCard
                        v-for="meeting in upcomingMeetings"
                        :key="meeting.id"
                        :meeting="meeting"
                        @edit="emit('edit-meeting', meeting)"
                        @delete="emit('delete-meeting', meeting)"
                    />
                </div>
            </section>

            <section class="mt-10">
                <h3 class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Past Meetings</h3>

                <div v-if="pastMeetings.length === 0" class="rounded-2xl border border-dashed border-slate-200 p-8 text-center dark:border-white/[0.07]">
                    <p class="text-xs text-slate-400">No past meetings.</p>
                </div>

                <div class="space-y-2">
                    <PastMeetingRow
                        v-for="meeting in pastMeetings"
                        :key="meeting.id"
                        :meeting="meeting"
                        @edit="emit('edit-meeting', meeting)"
                        @delete="emit('delete-meeting', meeting)"
                    />
                </div>
            </section>

        </div>
    </div>
</template>
