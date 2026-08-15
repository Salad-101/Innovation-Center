<script setup>
import { computed } from "vue"
import { useIdeasStore } from "../../stores/ideas"
import { formatTime } from "../../utils/formatters"

const props = defineProps({
    dateKey: { type: String, required: true },
    meetings: { type: Array, default: () => [] },
})

const emit = defineEmits(["schedule", "edit-meeting", "delete-meeting"])

const store = useIdeasStore()

const label = computed(() =>
    new Intl.DateTimeFormat("en", {
        weekday: "long",
        month: "long",
        day: "numeric",
        year: "numeric",
    }).format(new Date(`${props.dateKey}T00:00:00`))
)
</script>

<template>
    <section class="rounded-2xl border border-slate-200 bg-white p-5 dark:border-white/[0.07] dark:bg-[#15181f]">
        <div class="mb-4 flex items-center justify-between">
            <h3 class="text-sm font-semibold">{{ label }}</h3>
            <button @click="emit('schedule')" class="text-xs font-medium text-indigo-500">+ Schedule</button>
        </div>

        <div v-if="meetings.length === 0" class="rounded-xl border border-dashed border-slate-200 p-6 text-center dark:border-white/[0.06]">
            <p class="text-xs text-slate-400">No meetings on this day.</p>
        </div>

        <div v-else class="space-y-2">
            <div
                v-for="meeting in meetings"
                :key="meeting.id"
                class="group flex items-center justify-between rounded-xl border border-slate-200 px-4 py-3 dark:border-white/[0.06]"
            >
                <div class="min-w-0">
                    <p class="truncate text-xs font-medium">{{ store.getIdea(meeting.idea)?.title || "Unknown idea" }}</p>
                    <p class="mt-1 text-[10px] text-slate-400">
                        {{ formatTime(meeting.time) }}
                        <span v-if="meeting.location">· {{ meeting.location }}</span>
                    </p>
                </div>

                <div class="flex shrink-0 gap-1 opacity-0 transition group-hover:opacity-100">
                    <button @click="emit('edit-meeting', meeting)" class="rounded-lg px-2 py-1 text-[10px] text-indigo-500 hover:bg-indigo-500/10">Edit</button>
                    <button @click="emit('delete-meeting', meeting)" class="rounded-lg px-2 py-1 text-[10px] text-red-500 hover:bg-red-500/10">Delete</button>
                </div>
            </div>
        </div>
    </section>
</template>
