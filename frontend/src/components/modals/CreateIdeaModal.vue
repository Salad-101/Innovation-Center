<script setup>
import { reactive } from "vue"
import { useIdeasStore } from "../../stores/ideas"
import { PRIORITIES, PRIORITY_LABELS } from "../../constants/ideas"
import { getPriorityClass } from "../../utils/formatters"

const emit = defineEmits(["close"])

const store = useIdeasStore()

const form = reactive({
    title: "",
    description: "",
    priority: "MEDIUM",
})

async function save() {
    if (!form.title.trim()) {
        return
    }

    const created = await store.createIdea({ ...form })
    if (created) {
        emit("close")
    }
}
</script>

<template>
    <div class="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm" @click.self="emit('close')">
        <form @submit.prevent="save" class="w-full max-w-lg rounded-3xl bg-white shadow-2xl dark:bg-[#15181f]">

            <div class="flex items-center justify-between border-b border-slate-200 p-6 dark:border-white/[0.06]">
                <h2 class="text-lg font-semibold">New Idea</h2>
                <button type="button" @click="emit('close')" class="text-slate-400">✕</button>
            </div>

            <div class="space-y-4 p-6">

                <input v-model="form.title" required placeholder="Idea title" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 text-xs outline-none dark:border-white/[0.08] dark:bg-white/[0.03]" />

                <textarea v-model="form.description" rows="5" placeholder="Describe the idea..." class="w-full resize-none rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 text-xs outline-none dark:border-white/[0.08] dark:bg-white/[0.03]" />

                <div class="flex gap-2">
                    <button
                        v-for="priority in PRIORITIES"
                        :key="priority"
                        type="button"
                        @click="form.priority = priority"
                        :class="form.priority === priority ? getPriorityClass(priority) : 'border-slate-200 dark:border-white/[0.06]'"
                        class="flex-1 rounded-xl border px-3 py-2.5 text-xs"
                    >
                        {{ PRIORITY_LABELS[priority] }}
                    </button>
                </div>

            </div>

            <div class="flex justify-end gap-2 border-t border-slate-200 p-6 dark:border-white/[0.06]">
                <button type="button" @click="emit('close')" class="rounded-xl border border-slate-200 px-4 py-2.5 text-xs dark:border-white/[0.08]">Cancel</button>
                <button type="submit" class="rounded-xl bg-indigo-500 px-5 py-2.5 text-xs text-white">Create Idea</button>
            </div>

        </form>
    </div>
</template>
