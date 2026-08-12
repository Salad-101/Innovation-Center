<script setup>
import { computed, reactive } from "vue"
import { useIdeasStore } from "../../stores/ideas"

const props = defineProps({
    meeting: { type: Object, default: null }, // null = creating a new meeting
    ideaId: { type: [Number, String], default: null }, // pre-select an idea when scheduling from the idea modal
})

const emit = defineEmits(["close"])

const store = useIdeasStore()

const isEditing = computed(() => !!props.meeting)

const form = reactive({
    idea: props.meeting?.idea ?? props.ideaId ?? "",
    date: props.meeting?.date ?? "",
    time: props.meeting?.time ?? "",
    location: props.meeting?.location ?? "",
    notes: props.meeting?.notes ?? "",
})

async function save() {
    if (!form.idea || !form.date || !form.time) {
        store.error = "Idea, date and time are required."
        return
    }

    const saved = await store.saveMeeting(
        {
            idea: Number(form.idea),
            date: form.date,
            time: form.time,
            location: form.location,
            notes: form.notes,
        },
        props.meeting?.id ?? null
    )

    if (saved) {
        emit("close")
    }
}
</script>

<template>
    <div class="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm" @click.self="emit('close')">
        <form @submit.prevent="save" class="w-full max-w-lg rounded-3xl bg-white shadow-2xl dark:bg-[#15181f]">

            <div class="flex items-center justify-between border-b border-slate-200 p-6 dark:border-white/[0.06]">
                <div>
                    <h2 class="text-lg font-semibold">{{ isEditing ? "Edit Meeting" : "Schedule Meeting" }}</h2>
                    <p class="mt-1 text-xs text-slate-400">Meeting details</p>
                </div>
                <button type="button" @click="emit('close')" class="text-slate-400">✕</button>
            </div>

            <div class="space-y-4 p-6">

                <label class="block">
                    <span class="mb-1.5 block text-[10px] font-medium text-slate-400">Idea</span>
                    <select v-model="form.idea" required class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]">
                        <option value="" disabled>Select an idea</option>
                        <option v-for="idea in store.activeIdeas" :key="idea.id" :value="idea.id">{{ idea.title }}</option>
                    </select>
                </label>

                <div class="grid gap-4 sm:grid-cols-2">
                    <label class="block">
                        <span class="mb-1.5 block text-[10px] font-medium text-slate-400">Date</span>
                        <input v-model="form.date" type="date" required class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none dark:border-white/[0.08] dark:bg-white/[0.03]" />
                    </label>

                    <label class="block">
                        <span class="mb-1.5 block text-[10px] font-medium text-slate-400">Time</span>
                        <input v-model="form.time" type="time" required class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none dark:border-white/[0.08] dark:bg-white/[0.03]" />
                    </label>
                </div>

                <label class="block">
                    <span class="mb-1.5 block text-[10px] font-medium text-slate-400">Location</span>
                    <input v-model="form.location" placeholder="e.g. Innovation Lab" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]" />
                </label>

                <label class="block">
                    <span class="mb-1.5 block text-[10px] font-medium text-slate-400">Notes</span>
                    <textarea v-model="form.notes" rows="4" placeholder="Meeting agenda, discussion points, etc." class="w-full resize-none rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]" />
                </label>

            </div>

            <div class="flex justify-end gap-2 border-t border-slate-200 p-6 dark:border-white/[0.06]">
                <button type="button" @click="emit('close')" class="rounded-xl border border-slate-200 px-4 py-2.5 text-xs dark:border-white/[0.08]">Cancel</button>
                <button type="submit" class="rounded-xl bg-indigo-500 px-5 py-2.5 text-xs text-white">{{ isEditing ? "Save Changes" : "Schedule Meeting" }}</button>
            </div>

        </form>
    </div>
</template>
