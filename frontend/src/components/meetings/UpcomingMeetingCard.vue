<script setup>
import { useIdeasStore } from "../../stores/ideas"
import { formatTime, isMeetingToday } from "../../utils/formatters"

const props = defineProps({
    meeting: { type: Object, required: true },
})

defineEmits(["edit", "delete"])

const store = useIdeasStore()
</script>

<template>
    <div class="group rounded-2xl border border-slate-200 bg-white p-5 dark:border-white/[0.07] dark:bg-[#15181f]">

        <div class="flex items-start justify-between">

            <div class="flex items-start gap-4">

                <div
                    :class="isMeetingToday(meeting) ? 'bg-indigo-500 text-white' : 'bg-indigo-500/10 text-indigo-500'"
                    class="flex h-12 w-12 flex-col items-center justify-center rounded-xl"
                >
                    <span class="text-[9px] font-medium uppercase">
                        {{ new Date(`${meeting.date}T00:00:00`).toLocaleDateString("en", { month: "short" }) }}
                    </span>
                    <span class="text-lg font-bold leading-5">
                        {{ new Date(`${meeting.date}T00:00:00`).getDate() }}
                    </span>
                </div>

                <div>
                    <h4 class="text-sm font-semibold">{{ store.getIdea(meeting.idea)?.title || "Unknown Idea" }}</h4>

                    <p class="mt-1 text-xs text-slate-400">
                        {{ formatTime(meeting.time) }}
                        <span v-if="meeting.location">· {{ meeting.location }}</span>
                    </p>

                    <div class="mt-2 flex flex-wrap gap-1">
                        <span
                            v-for="student in store.getIdeaStudents(store.getIdea(meeting.idea))"
                            :key="student.id"
                            class="rounded-md bg-slate-100 px-2 py-1 text-[9px] text-slate-500 dark:bg-white/[0.05]"
                        >
                            {{ student.name }}
                        </span>
                    </div>
                </div>

            </div>

            <div class="flex gap-1 opacity-0 transition group-hover:opacity-100">
                <button @click="$emit('edit')" class="rounded-lg px-2 py-1 text-[10px] text-indigo-500 hover:bg-indigo-500/10">Edit</button>
                <button @click="$emit('delete')" class="rounded-lg px-2 py-1 text-[10px] text-red-500 hover:bg-red-500/10">Delete</button>
            </div>

        </div>

        <p v-if="meeting.notes" class="mt-4 border-t border-slate-100 pt-3 text-xs leading-5 text-slate-500 dark:border-white/[0.05] dark:text-slate-400">
            {{ meeting.notes }}
        </p>

    </div>
</template>
