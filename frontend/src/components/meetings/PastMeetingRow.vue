<script setup>
import { useIdeasStore } from "../../stores/ideas"
import { formatDate, formatTime } from "../../utils/formatters"

defineProps({
    meeting: { type: Object, required: true },
})

defineEmits(["edit", "delete"])

const store = useIdeasStore()
</script>

<template>
    <div class="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-4 py-3 opacity-70 dark:border-white/[0.06] dark:bg-[#15181f]">

        <div>
            <p class="text-xs font-medium">{{ store.getIdea(meeting.idea)?.title || "Unknown Idea" }}</p>
            <p class="mt-1 text-[10px] text-slate-400">{{ formatDate(meeting.date) }} · {{ formatTime(meeting.time) }}</p>
        </div>

        <div class="flex gap-1">
            <button @click="$emit('edit')" class="rounded-lg px-2 py-1 text-[10px] text-indigo-500">Edit</button>
            <button @click="$emit('delete')" class="rounded-lg px-2 py-1 text-[10px] text-red-500">Delete</button>
        </div>

    </div>
</template>
