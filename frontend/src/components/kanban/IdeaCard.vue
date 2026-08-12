<script setup>
import { useIdeasStore } from "../../stores/ideas"
import { getInitials, getPriorityClass } from "../../utils/formatters"
import { PRIORITY_LABELS } from "../../constants/ideas"

defineProps({
    idea: { type: Object, required: true },
    showArchived: { type: Boolean, default: false },
})

const emit = defineEmits(["dragstart", "dragend", "select", "unarchive"])

const store = useIdeasStore()
</script>

<template>
    <article
        draggable="true"
        @dragstart="event => emit('dragstart', event)"
        @dragend="emit('dragend')"
        @click="emit('select')"
        class="group cursor-grab rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-300 hover:shadow-lg dark:border-white/[0.07] dark:bg-[#15181f] dark:hover:border-indigo-500/40"
    >

        <div class="mb-3 flex justify-between">
            <span :class="getPriorityClass(idea.priority)" class="rounded-md border px-2 py-1 text-[9px] font-semibold uppercase">
                {{ PRIORITY_LABELS[idea.priority] }}
            </span>
        </div>

        <h3 class="text-sm font-semibold">{{ idea.title }}</h3>

        <p class="mt-2 line-clamp-3 text-xs leading-5 text-slate-500 dark:text-slate-400">
            {{ idea.description }}
        </p>

        <div v-if="idea.students?.length" class="mt-4 flex items-center">
            <div class="flex -space-x-2">
                <div
                    v-for="studentId in idea.students.slice(0, 4)"
                    :key="studentId"
                    class="flex h-7 w-7 items-center justify-center rounded-full border-2 border-white bg-indigo-500 text-[8px] font-semibold text-white dark:border-[#15181f]"
                >
                    {{ getInitials(store.getStudent(studentId)?.name) }}
                </div>
            </div>

            <span class="ml-2 text-[10px] text-slate-400">{{ idea.students.length }} students</span>
        </div>

        <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-3 text-[10px] text-slate-400 dark:border-white/[0.05]">
            <span>📅 {{ store.getIdeaMeetings(idea).length }} meetings</span>

            <button
                v-if="showArchived"
                @click.stop="emit('unarchive')"
                class="rounded-lg px-2.5 py-1.5 text-[10px] font-medium text-indigo-500 transition hover:bg-indigo-500/10"
            >
                Unarchive
            </button>

            <span v-else class="text-indigo-500 opacity-0 transition group-hover:opacity-100">View →</span>
        </div>

    </article>
</template>
