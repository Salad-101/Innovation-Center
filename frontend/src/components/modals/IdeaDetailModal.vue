<script setup>
import { useIdeasStore } from "../../stores/ideas"
import { getInitials, formatDate, formatTime, formatDateTime, getPriorityClass } from "../../utils/formatters"
import { STATUSES, STATUS_LABELS, PRIORITIES, PRIORITY_LABELS, FIELD_LABELS } from "../../constants/ideas"

const props = defineProps({
    idea: { type: Object, required: true },
})

const emit = defineEmits(["close", "schedule-meeting", "edit-meeting", "delete-meeting"])

const store = useIdeasStore()

function toggleStudent(studentId) {
    const current = [...(props.idea.students || [])]
    const exists = current.includes(studentId)

    const updated = exists
        ? current.filter(id => id !== studentId)
        : [...current, studentId]

    store.updateIdeaStudents(props.idea, updated)
}

async function archive() {
    const archived = await store.archiveIdea(props.idea)
    if (archived) {
        emit("close")
    }
}

// Renders a human-readable line for one IdeaChangeLog entry. status/priority
// values are stored as raw codes (e.g. "REVIEW"), so translate those through
// the shared label maps; students/title/description already arrive as
// display-ready text from the API.
function describeChange(log) {
    const label = FIELD_LABELS[log.field] || log.field

    if (log.field === "status") {
        return `${label} changed from "${STATUS_LABELS[log.old_value] ?? log.old_value}" to "${STATUS_LABELS[log.new_value] ?? log.new_value}"`
    }

    if (log.field === "priority") {
        return `${label} changed from "${PRIORITY_LABELS[log.old_value] ?? log.old_value}" to "${PRIORITY_LABELS[log.new_value] ?? log.new_value}"`
    }

    if (log.field === "is_archived") {
        return log.new_value === "True" ? "Idea archived" : "Idea unarchived"
    }

    return `${label} changed from "${log.old_value || "(empty)"}" to "${log.new_value || "(empty)"}"`
}
</script>

<template>
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm" @click.self="emit('close')">
        <div class="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-3xl bg-white shadow-2xl dark:bg-[#15181f]">

            <div class="sticky top-0 z-10 flex items-start justify-between border-b border-slate-200 bg-white/95 p-6 backdrop-blur dark:border-white/[0.06] dark:bg-[#15181f]/95">
                <div>
                    <div class="mb-3 flex gap-2">
                        <span class="rounded-md bg-slate-100 px-2 py-1 text-[10px] dark:bg-white/[0.05]">{{ STATUS_LABELS[idea.status] }}</span>
                        <span :class="getPriorityClass(idea.priority)" class="rounded-md border px-2 py-1 text-[10px] uppercase">{{ PRIORITY_LABELS[idea.priority] }}</span>
                    </div>
                    <h2 class="text-xl font-semibold">{{ idea.title }}</h2>
                </div>

                <button @click="emit('close')" class="text-slate-400">✕</button>
            </div>

            <div class="space-y-7 p-6">

                <section>
                    <h3 class="mb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400">Description</h3>
                    <p class="text-sm leading-6 text-slate-600 dark:text-slate-300">{{ idea.description }}</p>
                </section>

                <section>
                    <div class="mb-3 flex items-center justify-between">
                        <h3 class="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Students</h3>
                        <span class="text-[10px] text-slate-400">{{ store.getIdeaStudents(idea).length }} assigned</span>
                    </div>

                    <div class="grid gap-2 sm:grid-cols-2">
                        <button
                            v-for="student in store.students"
                            :key="student.id"
                            @click="toggleStudent(student.id)"
                            :class="idea.students?.includes(student.id) ? 'border-indigo-500 bg-indigo-500/10' : 'border-slate-200 dark:border-white/[0.06]'"
                            class="flex items-center gap-3 rounded-xl border p-3 text-left transition"
                        >
                            <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-500/10 text-[10px] font-semibold text-indigo-500">
                                {{ getInitials(student.name) }}
                            </div>

                            <div class="min-w-0">
                                <p class="truncate text-xs font-medium">{{ student.name }}</p>
                                <p class="truncate text-[10px] text-slate-400">{{ student.student_id }}</p>
                            </div>

                            <span v-if="idea.students?.includes(student.id)" class="ml-auto text-indigo-500">✓</span>
                        </button>
                    </div>
                </section>

                <section>
                    <h3 class="mb-3 text-[10px] font-semibold uppercase tracking-wider text-slate-400">Status</h3>
                    <div class="flex flex-wrap gap-2">
                        <button
                            v-for="status in STATUSES"
                            :key="status"
                            @click="store.updateStatus(idea, status)"
                            :class="idea.status === status ? 'bg-indigo-500 text-white' : 'border border-slate-200 dark:border-white/[0.07]'"
                            class="rounded-lg px-3 py-2 text-xs"
                        >
                            {{ STATUS_LABELS[status] }}
                        </button>
                    </div>
                </section>

                <section>
                    <h3 class="mb-3 text-[10px] font-semibold uppercase tracking-wider text-slate-400">Priority</h3>
                    <div class="flex gap-2">
                        <button
                            v-for="priority in PRIORITIES"
                            :key="priority"
                            @click="store.updatePriority(idea, priority)"
                            :class="idea.priority === priority ? getPriorityClass(priority) : 'border-slate-200 dark:border-white/[0.06]'"
                            class="rounded-lg border px-3 py-2 text-xs"
                        >
                            {{ PRIORITY_LABELS[priority] }}
                        </button>
                    </div>
                </section>

                <section>
                    <div class="mb-3 flex items-center justify-between">
                        <h3 class="text-[10px] font-semibold uppercase tracking-wider text-slate-400">Meetings</h3>
                        <button @click="emit('schedule-meeting', idea)" class="text-xs font-medium text-indigo-500">+ Schedule</button>
                    </div>

                    <div v-if="store.getIdeaMeetings(idea).length" class="space-y-2">
                        <div v-for="meeting in store.getIdeaMeetings(idea)" :key="meeting.id" class="group rounded-xl border border-slate-200 p-4 dark:border-white/[0.06]">
                            <div class="flex items-center justify-between">
                                <div>
                                    <p class="text-xs font-medium">{{ formatDate(meeting.date) }} · {{ formatTime(meeting.time) }}</p>
                                    <p class="mt-1 text-[10px] text-slate-400">{{ meeting.location || "No location" }}</p>
                                </div>

                                <div class="flex gap-1 opacity-0 group-hover:opacity-100">
                                    <button @click="emit('edit-meeting', meeting)" class="text-[10px] text-indigo-500">Edit</button>
                                    <button @click="emit('delete-meeting', meeting)" class="text-[10px] text-red-500">Delete</button>
                                </div>
                            </div>

                            <p v-if="meeting.notes" class="mt-3 text-xs text-slate-500">{{ meeting.notes }}</p>
                        </div>
                    </div>

                    <div v-else class="rounded-xl border border-dashed border-slate-200 p-5 text-center dark:border-white/[0.06]">
                        <p class="text-xs text-slate-400">No meetings scheduled.</p>
                    </div>
                </section>

                <section>
                    <h3 class="mb-3 text-[10px] font-semibold uppercase tracking-wider text-slate-400">History</h3>

                    <div v-if="idea.change_logs?.length" class="space-y-2">
                        <div
                            v-for="log in idea.change_logs"
                            :key="log.id"
                            class="flex items-start justify-between gap-3 rounded-xl border border-slate-200 px-4 py-3 dark:border-white/[0.06]"
                        >
                            <p class="text-xs text-slate-600 dark:text-slate-300">{{ describeChange(log) }}</p>
                            <span class="shrink-0 text-[10px] text-slate-400">{{ formatDateTime(log.changed_at) }}</span>
                        </div>
                    </div>

                    <div v-else class="rounded-xl border border-dashed border-slate-200 p-5 text-center dark:border-white/[0.06]">
                        <p class="text-xs text-slate-400">No changes yet.</p>
                    </div>
                </section>

            </div>

            <div class="flex justify-between border-t border-slate-200 p-6 dark:border-white/[0.06]">
                <button @click="archive" class="text-xs text-red-500">Archive Idea</button>
                <button @click="emit('close')" class="rounded-xl bg-indigo-500 px-5 py-2.5 text-xs text-white">Done</button>
            </div>

        </div>
    </div>
</template>
