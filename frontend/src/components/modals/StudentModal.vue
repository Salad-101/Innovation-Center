<script setup>
import { computed, reactive } from "vue"
import { useIdeasStore } from "../../stores/ideas"

const props = defineProps({
    student: { type: Object, default: null }, // null = creating a new student
})

const emit = defineEmits(["close"])

const store = useIdeasStore()

const isEditing = computed(() => !!props.student)

const form = reactive({
    student_id: props.student?.student_id ?? "",
    name: props.student?.name ?? "",
    email: props.student?.email ?? "",
    phone: props.student?.phone ?? "",
    department: props.student?.department ?? "",
})

async function save() {
    const saved = await store.saveStudent({ ...form }, props.student?.id ?? null)
    if (saved) {
        emit("close")
    }
}

async function remove() {
    if (!confirm(`Delete ${props.student.name}?`)) {
        return
    }

    const deleted = await store.deleteStudent(props.student)
    if (deleted) {
        emit("close")
    }
}
</script>

<template>
    <div class="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm" @click.self="emit('close')">
        <form @submit.prevent="save" class="w-full max-w-lg rounded-3xl bg-white shadow-2xl dark:bg-[#15181f]">

            <div class="flex items-center justify-between border-b border-slate-200 p-6 dark:border-white/[0.06]">
                <div>
                    <h2 class="text-lg font-semibold">{{ isEditing ? "Edit Student" : "Add Student" }}</h2>
                    <p class="mt-1 text-xs text-slate-400">Student information</p>
                </div>
                <button type="button" @click="emit('close')" class="text-slate-400">✕</button>
            </div>

            <div class="space-y-4 p-6">

                <div class="grid gap-4 sm:grid-cols-2">
                    <label class="block">
                        <span class="mb-1.5 block text-[10px] font-medium text-slate-400">Student ID</span>
                        <input v-model="form.student_id" required class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]" />
                    </label>

                    <label class="block">
                        <span class="mb-1.5 block text-[10px] font-medium text-slate-400">Name</span>
                        <input v-model="form.name" required class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]" />
                    </label>
                </div>

                <label class="block">
                    <span class="mb-1.5 block text-[10px] font-medium text-slate-400">Email</span>
                    <input v-model="form.email" type="email" required class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]" />
                </label>

                <div class="grid gap-4 sm:grid-cols-2">
                    <label class="block">
                        <span class="mb-1.5 block text-[10px] font-medium text-slate-400">Phone</span>
                        <input v-model="form.phone" class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]" />
                    </label>

                    <label class="block">
                        <span class="mb-1.5 block text-[10px] font-medium text-slate-400">Department</span>
                        <input v-model="form.department" required class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]" />
                    </label>
                </div>

            </div>

            <div class="flex justify-between border-t border-slate-200 p-6 dark:border-white/[0.06]">
                <button v-if="isEditing" type="button" @click="remove" class="text-xs text-red-500">Delete Student</button>
                <span v-else></span>

                <div class="flex gap-2">
                    <button type="button" @click="emit('close')" class="rounded-xl border border-slate-200 px-4 py-2.5 text-xs dark:border-white/[0.08]">Cancel</button>
                    <button type="submit" class="rounded-xl bg-indigo-500 px-5 py-2.5 text-xs text-white">{{ isEditing ? "Save Changes" : "Add Student" }}</button>
                </div>
            </div>

        </form>
    </div>
</template>
