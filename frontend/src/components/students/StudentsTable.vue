<script setup>
import { computed, ref } from "vue"
import { useIdeasStore } from "../../stores/ideas"
import { getInitials } from "../../utils/formatters"

const emit = defineEmits(["edit-student"])

const store = useIdeasStore()

const studentSearch = ref("")

const filteredStudents = computed(() => {
    if (!studentSearch.value.trim()) {
        return store.students
    }

    const query = studentSearch.value.trim().toLowerCase()

    return store.students.filter(student =>
        student.name?.toLowerCase().includes(query) ||
        student.student_id?.toLowerCase().includes(query) ||
        student.email?.toLowerCase().includes(query) ||
        student.department?.toLowerCase().includes(query)
    )
})
</script>

<template>
    <div class="min-h-0 flex-1 overflow-auto p-6">
        <div class="mx-auto max-w-6xl">

            <div class="mb-5 flex items-center justify-between">
                <div>
                    <h2 class="text-lg font-semibold">Students</h2>
                    <p class="mt-1 text-xs text-slate-400">Manage students participating in ideas.</p>
                </div>

                <input
                    v-model="studentSearch"
                    type="text"
                    placeholder="Search students..."
                    class="h-9 w-64 rounded-xl border border-slate-200 bg-white px-3 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
                />
            </div>

            <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-white/[0.07] dark:bg-[#15181f]">

                <div class="grid grid-cols-[2fr_1fr_2fr_1.5fr_80px] border-b border-slate-200 bg-slate-50 px-5 py-3 text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:border-white/[0.06] dark:bg-white/[0.02]">
                    <span>Name</span>
                    <span>Student ID</span>
                    <span>Email</span>
                    <span>Department</span>
                    <span></span>
                </div>

                <div v-if="filteredStudents.length === 0" class="p-12 text-center">
                    <p class="text-sm text-slate-400">No students found.</p>
                </div>

                <div
                    v-for="student in filteredStudents"
                    :key="student.id"
                    @click="emit('edit-student', student)"
                    class="grid cursor-pointer grid-cols-[2fr_1fr_2fr_1.5fr_80px] items-center border-b border-slate-100 px-5 py-4 transition last:border-0 hover:bg-slate-50 dark:border-white/[0.04] dark:hover:bg-white/[0.02]"
                >

                    <div class="flex items-center gap-3">
                        <div class="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-500/10 text-xs font-semibold text-indigo-500">
                            {{ getInitials(student.name) }}
                        </div>

                        <div>
                            <p class="text-xs font-medium">{{ student.name }}</p>
                            <p class="text-[10px] text-slate-400">{{ store.getStudentIdeas(student).length }} ideas</p>
                        </div>
                    </div>

                    <span class="text-xs text-slate-500">{{ student.student_id }}</span>
                    <span class="truncate text-xs text-slate-500">{{ student.email }}</span>
                    <span class="truncate text-xs text-slate-500">{{ student.department }}</span>

                    <div class="flex justify-end">
                        <button @click.stop="emit('edit-student', student)" class="rounded-lg px-2 py-1 text-[10px] text-indigo-500 hover:bg-indigo-500/10">
                            Edit
                        </button>
                    </div>

                </div>

            </div>

        </div>
    </div>
</template>
