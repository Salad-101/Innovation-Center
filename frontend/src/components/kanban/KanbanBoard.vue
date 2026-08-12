<script setup>
import { computed, ref } from "vue"
import { useIdeasStore } from "../../stores/ideas"
import { STATUSES, STATUS_LABELS, STATUS_DESCRIPTIONS, PRIORITY_LABELS } from "../../constants/ideas"
import KanbanColumn from "./KanbanColumn.vue"

const emit = defineEmits(["select-idea"])

const store = useIdeasStore()

const searchQuery = ref("")
const selectedPriority = ref("ALL")
const showArchived = ref(false)
const draggedIdea = ref(null)

const priorityFilters = ["ALL", "HIGH", "MEDIUM", "LOW"]

const filteredIdeas = computed(() => {
    let result = showArchived.value ? store.archivedIdeas : store.activeIdeas

    if (searchQuery.value.trim()) {
        const query = searchQuery.value.trim().toLowerCase()

        result = result.filter(idea =>
            idea.title?.toLowerCase().includes(query) ||
            idea.description?.toLowerCase().includes(query)
        )
    }

    if (selectedPriority.value !== "ALL") {
        result = result.filter(idea => idea.priority === selectedPriority.value)
    }

    return result
})

const ideasByStatus = computed(() => {
    const groups = {}

    for (const status of STATUSES) {
        groups[status] = filteredIdeas.value.filter(idea => idea.status === status)
    }

    return groups
})

function startDrag(idea, event) {
    draggedIdea.value = idea
    event.dataTransfer.effectAllowed = "move"
    event.dataTransfer.setData("text/plain", String(idea.id))
}

function endDrag() {
    draggedIdea.value = null
}

async function dropIdea(status) {
    if (!draggedIdea.value) {
        return
    }

    const idea = draggedIdea.value
    draggedIdea.value = null

    await store.updateStatus(idea, status)
}
</script>

<template>
    <div class="shrink-0 border-b border-slate-200 px-6 py-4 dark:border-white/[0.06]">
        <div class="flex flex-wrap items-center gap-3">

            <input
                v-model="searchQuery"
                type="text"
                placeholder="Search ideas..."
                class="h-9 w-64 rounded-xl border border-slate-200 bg-white pl-3 pr-3 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
            />

            <button
                v-for="priority in priorityFilters"
                :key="priority"
                @click="selectedPriority = priority"
                :class="selectedPriority === priority
                    ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
                    : 'bg-slate-100 text-slate-500 dark:bg-white/[0.04] dark:text-slate-400'"
                class="rounded-lg px-3 py-2 text-[10px] font-medium"
            >
                {{ priority === "ALL" ? "All" : PRIORITY_LABELS[priority] }}
            </button>

            <button
                @click="showArchived = !showArchived"
                :class="showArchived
                    ? 'bg-indigo-500 text-white'
                    : 'bg-slate-100 text-slate-500 dark:bg-white/[0.04] dark:text-slate-400'"
                class="ml-auto rounded-lg px-3 py-2 text-[10px] font-medium"
            >
                Archived {{ store.archivedIdeas.length }}
            </button>

        </div>
    </div>

    <div class="min-h-0 flex-1 overflow-auto p-6">
        <div class="flex min-w-max gap-5 pb-6">
            <KanbanColumn
                v-for="status in STATUSES"
                :key="status"
                :status="status"
                :label="STATUS_LABELS[status]"
                :description="STATUS_DESCRIPTIONS[status]"
                :ideas="ideasByStatus[status]"
                :show-archived="showArchived"
                @dragstart-idea="startDrag"
                @dragend-idea="endDrag"
                @drop="dropIdea(status)"
                @select-idea="idea => emit('select-idea', idea)"
                @unarchive-idea="store.unarchiveIdea"
            />
        </div>
    </div>
</template>
