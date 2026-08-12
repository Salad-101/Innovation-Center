<script setup>
import { computed, onMounted, ref, watch } from "vue"
import { useIdeasStore } from "./stores/ideas"
import { getLocalToday } from "./utils/formatters"

import AppHeader from "./components/layout/AppHeader.vue"
import KanbanBoard from "./components/kanban/KanbanBoard.vue"
import StudentsTable from "./components/students/StudentsTable.vue"
import MeetingsView from "./components/meetings/MeetingsView.vue"
import IdeaDetailModal from "./components/modals/IdeaDetailModal.vue"
import StudentModal from "./components/modals/StudentModal.vue"
import MeetingModal from "./components/modals/MeetingModal.vue"
import CreateIdeaModal from "./components/modals/CreateIdeaModal.vue"

const store = useIdeasStore()

const currentView = ref("kanban")

const darkMode = ref(
    localStorage.getItem("innovation-center-dark-mode") === "true"
)

watch(darkMode, (value) => {
    localStorage.setItem(
        "innovation-center-dark-mode",
        value
    )
})

const selectedIdea = ref(null)

const showCreateIdeaModal = ref(false)

const showStudentModal = ref(false)
const editingStudent = ref(null) // null = creating

const showMeetingModal = ref(false)
const editingMeeting = ref(null) // null = creating
const meetingIdeaId = ref(null) // pre-selected idea when scheduling from a card/modal

const upcomingMeetingsCount = computed(() =>
    store.meetings.filter(meeting => meeting.date >= getLocalToday()).length
)

function handleCreate() {
    if (currentView.value === "kanban") {
        showCreateIdeaModal.value = true
    } else if (currentView.value === "students") {
        openCreateStudent()
    } else if (currentView.value === "meetings") {
        openCreateMeeting()
    }
}

function selectIdea(idea) {
    selectedIdea.value = idea
}

function closeIdeaModal() {
    selectedIdea.value = null
}

function openCreateStudent() {
    editingStudent.value = null
    showStudentModal.value = true
}

function openEditStudent(student) {
    editingStudent.value = student
    showStudentModal.value = true
}

function closeStudentModal() {
    showStudentModal.value = false
    editingStudent.value = null
}

function openCreateMeeting(idea = null) {
    editingMeeting.value = null
    meetingIdeaId.value = idea?.id ?? null
    showMeetingModal.value = true
}

function openEditMeeting(meeting) {
    editingMeeting.value = meeting
    meetingIdeaId.value = null
    showMeetingModal.value = true
}

function closeMeetingModal() {
    showMeetingModal.value = false
    editingMeeting.value = null
    meetingIdeaId.value = null
}

async function handleDeleteMeeting(meeting) {
    if (!confirm("Delete this meeting?")) {
        return
    }

    await store.deleteMeeting(meeting)
}

onMounted(store.fetchData)
</script>

<template>
    <div :class="{ dark: darkMode }" class="h-screen">
        <main class="flex h-full flex-col overflow-hidden bg-slate-50 text-slate-900 dark:bg-[#0d0f14] dark:text-slate-100">

            <AppHeader
                :current-view="currentView"
                :dark-mode="darkMode"
                :students-count="store.students.length"
                :upcoming-meetings-count="upcomingMeetingsCount"
                @change-view="view => currentView = view"
                @toggle-dark-mode="darkMode = !darkMode"
                @create="handleCreate"
            />

            <div v-if="store.error" class="mx-6 mt-4 shrink-0 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-xs text-red-500">
                {{ store.error }}
                <button @click="store.error = null" class="ml-3 font-medium underline">Dismiss</button>
            </div>

            <div v-if="store.loading" class="flex flex-1 items-center justify-center">
                <div class="text-center">
                    <div class="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-slate-200 border-t-indigo-500 dark:border-white/10 dark:border-t-indigo-400" />
                    <p class="mt-3 text-xs text-slate-400">Loading...</p>
                </div>
            </div>

            <template v-else-if="currentView === 'kanban'">
                <KanbanBoard @select-idea="selectIdea" />
            </template>

            <template v-else-if="currentView === 'students'">
                <StudentsTable @edit-student="openEditStudent" />
            </template>

            <template v-else-if="currentView === 'meetings'">
                <MeetingsView @edit-meeting="openEditMeeting" @delete-meeting="handleDeleteMeeting" />
            </template>

            <IdeaDetailModal
                v-if="selectedIdea"
                :idea="selectedIdea"
                @close="closeIdeaModal"
                @schedule-meeting="openCreateMeeting"
                @edit-meeting="openEditMeeting"
                @delete-meeting="handleDeleteMeeting"
            />

            <StudentModal v-if="showStudentModal" :student="editingStudent" @close="closeStudentModal" />

            <MeetingModal v-if="showMeetingModal" :meeting="editingMeeting" :idea-id="meetingIdeaId" @close="closeMeetingModal" />

            <CreateIdeaModal v-if="showCreateIdeaModal" @close="showCreateIdeaModal = false" />

        </main>
    </div>
</template>
