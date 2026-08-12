<script setup>
import { getStatusDotClass } from "../../utils/formatters"
import IdeaCard from "./IdeaCard.vue"

defineProps({
    status: { type: String, required: true },
    label: { type: String, required: true },
    description: { type: String, required: true },
    ideas: { type: Array, required: true },
    showArchived: { type: Boolean, default: false },
})

const emit = defineEmits(["dragstart-idea", "dragend-idea", "drop", "select-idea", "unarchive-idea"])
</script>

<template>
    <section @dragover.prevent @drop="emit('drop')" class="flex w-72 flex-col">

        <div class="mb-1 flex items-center gap-2">
            <span class="h-2.5 w-2.5 rounded-full" :class="getStatusDotClass(status)" />
            <h2 class="text-sm font-semibold">{{ label }}</h2>
            <span class="rounded-md bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-500 dark:bg-white/[0.05]">
                {{ ideas.length }}
            </span>
        </div>

        <p class="mb-3 text-[10px] text-slate-400">{{ description }}</p>

        <div class="space-y-3">

            <IdeaCard
                v-for="idea in ideas"
                :key="idea.id"
                :idea="idea"
                :show-archived="showArchived"
                @dragstart="event => emit('dragstart-idea', idea, event)"
                @dragend="emit('dragend-idea')"
                @select="emit('select-idea', idea)"
                @unarchive="emit('unarchive-idea', idea)"
            />

            <div
                v-if="ideas.length === 0"
                class="flex min-h-28 items-center justify-center rounded-2xl border border-dashed border-slate-200 dark:border-white/[0.07]"
            >
                <span class="text-[10px] text-slate-400">Drop ideas here</span>
            </div>

        </div>

    </section>
</template>
