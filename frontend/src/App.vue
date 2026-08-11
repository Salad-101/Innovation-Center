```vue
<script setup>
import { computed, onMounted, ref } from "vue"

const API_URL = "http://127.0.0.1:8000/api"

// ============================================================
// APPLICATION STATE
// ============================================================

const currentView = ref("kanban")

const ideas = ref([])
const students = ref([])
const meetings = ref([])

const loading = ref(true)
const error = ref(null)

const selectedIdea = ref(null)
const selectedStudent = ref(null)

const darkMode = ref(true)


// ============================================================
// KANBAN STATE
// ============================================================

const searchQuery = ref("")
const selectedPriority = ref("ALL")
const showArchived = ref(false)
const draggedIdea = ref(null)


// ============================================================
// STUDENT STATE
// ============================================================

const studentSearch = ref("")
const showStudentModal = ref(false)
const editingStudent = ref(false)

const studentForm = ref({
    student_id: "",
    name: "",
    email: "",
    phone: "",
    department: "",
})


// ============================================================
// MEETING STATE
// ============================================================

const meetingSearch = ref("")
const showMeetingModal = ref(false)
const editingMeeting = ref(false)

const meetingForm = ref({
    id: null,
    idea: "",
    date: "",
    time: "",
    location: "",
    notes: "",
})


// ============================================================
// CREATE IDEA
// ============================================================

const showCreateModal = ref(false)

const newIdea = ref({
    title: "",
    description: "",
    priority: "MEDIUM",
})


// ============================================================
// KANBAN CONFIG
// ============================================================

const statuses = [
    "NEW",
    "REVIEW",
    "REFINEMENT",
    "APPROVED",
    "REJECTED",
]

const statusLabels = {
    NEW: "New",
    REVIEW: "Under Review",
    REFINEMENT: "Needs Refinement",
    APPROVED: "Approved",
    REJECTED: "Rejected",
}

const statusDescriptions = {
    NEW: "Recently submitted ideas",
    REVIEW: "Ideas being evaluated",
    REFINEMENT: "Ideas that need improvement",
    APPROVED: "Ideas ready to move forward",
    REJECTED: "Ideas that were rejected",
}

const priorityLabels = {
    LOW: "Low",
    MEDIUM: "Medium",
    HIGH: "High",
}


// ============================================================
// COMPUTED
// ============================================================

const activeIdeas = computed(() =>
    ideas.value.filter(idea => !idea.is_archived)
)

const archivedIdeas = computed(() =>
    ideas.value.filter(idea => idea.is_archived)
)

const filteredIdeas = computed(() => {
    let result = showArchived.value
        ? archivedIdeas.value
        : activeIdeas.value

    if (searchQuery.value.trim()) {
        const query = searchQuery.value.trim().toLowerCase()

        result = result.filter(idea =>
            idea.title?.toLowerCase().includes(query) ||
            idea.description?.toLowerCase().includes(query)
        )
    }

    if (selectedPriority.value !== "ALL") {
        result = result.filter(
            idea => idea.priority === selectedPriority.value
        )
    }

    return result
})

const ideasByStatus = computed(() => {
    const groups = {}

    for (const status of statuses) {
        groups[status] = filteredIdeas.value.filter(
            idea => idea.status === status
        )
    }

    return groups
})

const upcomingMeetings = computed(() => {
    const today = new Date().toISOString().split("T")[0]

    return [...meetings.value]
        .filter(meeting => meeting.date >= today)
        .sort((a, b) => {
            return `${a.date} ${a.time}`.localeCompare(
                `${b.date} ${b.time}`
            )
        })
})

const pastMeetings = computed(() => {
    const today = new Date().toISOString().split("T")[0]

    return [...meetings.value]
        .filter(meeting => meeting.date < today)
        .sort((a, b) => {
            return `${b.date} ${b.time}`.localeCompare(
                `${a.date} ${a.time}`
            )
        })
})

const filteredStudents = computed(() => {
    if (!studentSearch.value.trim()) {
        return students.value
    }

    const query = studentSearch.value.trim().toLowerCase()

    return students.value.filter(student =>
        student.name?.toLowerCase().includes(query) ||
        student.student_id?.toLowerCase().includes(query) ||
        student.email?.toLowerCase().includes(query) ||
        student.department?.toLowerCase().includes(query)
    )
})

const filteredMeetings = computed(() => {
    if (!meetingSearch.value.trim()) {
        return meetings.value
    }

    const query = meetingSearch.value.trim().toLowerCase()

    return meetings.value.filter(meeting => {
        const idea = getIdea(meeting.idea)

        return (
            idea?.title?.toLowerCase().includes(query) ||
            meeting.location?.toLowerCase().includes(query) ||
            meeting.notes?.toLowerCase().includes(query)
        )
    })
})


// ============================================================
// STATISTICS
// ============================================================

const totalIdeas = computed(() => activeIdeas.value.length)

const reviewCount = computed(() =>
    activeIdeas.value.filter(
        idea => idea.status === "REVIEW"
    ).length
)

const refinementCount = computed(() =>
    activeIdeas.value.filter(
        idea => idea.status === "REFINEMENT"
    ).length
)

const approvedCount = computed(() =>
    activeIdeas.value.filter(
        idea => idea.status === "APPROVED"
    ).length
)


// ============================================================
// FETCH DATA
// ============================================================

async function fetchData() {
    loading.value = true
    error.value = null

    try {
        const [
            ideasResponse,
            studentsResponse,
            meetingsResponse,
        ] = await Promise.all([
            fetch(`${API_URL}/ideas/`),
            fetch(`${API_URL}/students/`),
            fetch(`${API_URL}/meetings/`),
        ])

        if (!ideasResponse.ok) {
            throw new Error(
                `Ideas request failed: ${ideasResponse.status}`
            )
        }

        if (!studentsResponse.ok) {
            throw new Error(
                `Students request failed: ${studentsResponse.status}`
            )
        }

        if (!meetingsResponse.ok) {
            throw new Error(
                `Meetings request failed: ${meetingsResponse.status}`
            )
        }

        ideas.value = await ideasResponse.json()
        students.value = await studentsResponse.json()
        meetings.value = await meetingsResponse.json()

    } catch (err) {
        console.error(err)
        error.value = err.message
    } finally {
        loading.value = false
    }
}


// ============================================================
// LOOKUPS
// ============================================================

function getIdea(id) {
    return ideas.value.find(idea => idea.id === id)
}

function getStudent(id) {
    return students.value.find(student => student.id === id)
}

function getIdeaStudents(idea) {
    if (!idea?.students) {
        return []
    }

    return idea.students
        .map(id => getStudent(id))
        .filter(Boolean)
}

function getIdeaMeetings(idea) {
    if (!idea) {
        return []
    }

    return meetings.value.filter(
        meeting => meeting.idea === idea.id
    )
}

function getStudentIdeas(student) {
    if (!student) {
        return []
    }

    return ideas.value.filter(
        idea => idea.students?.includes(student.id)
    )
}

function getInitials(name) {
    if (!name) {
        return "?"
    }

    return name
        .split(" ")
        .map(part => part[0])
        .join("")
        .slice(0, 2)
        .toUpperCase()
}


// ============================================================
// FORMATTING
// ============================================================

function formatDate(date) {
    if (!date) {
        return ""
    }

    return new Intl.DateTimeFormat("en", {
        month: "short",
        day: "numeric",
        year: "numeric",
    }).format(new Date(`${date}T00:00:00`))
}

function formatTime(time) {
    if (!time) {
        return ""
    }

    const [hours, minutes] = time.split(":")

    const date = new Date()

    date.setHours(Number(hours), Number(minutes))

    return new Intl.DateTimeFormat("en", {
        hour: "numeric",
        minute: "2-digit",
    }).format(date)
}

function isMeetingToday(meeting) {
    const today = new Date()
        .toISOString()
        .split("T")[0]

    return meeting.date === today
}

function getStatusDotClass(status) {
    return {
        NEW: "bg-blue-500",
        REVIEW: "bg-amber-500",
        REFINEMENT: "bg-orange-500",
        APPROVED: "bg-emerald-500",
        REJECTED: "bg-red-500",
    }[status]
}

function getPriorityClass(priority) {
    return {
        LOW:
            "border-slate-500/20 bg-slate-500/10 text-slate-500 dark:text-slate-400",

        MEDIUM:
            "border-amber-500/20 bg-amber-500/10 text-amber-600 dark:text-amber-400",

        HIGH:
            "border-red-500/20 bg-red-500/10 text-red-600 dark:text-red-400",
    }[priority]
}


// ============================================================
// IDEA MANAGEMENT
// ============================================================

function selectIdea(idea) {
    selectedIdea.value = idea
}

function closeIdea() {
    selectedIdea.value = null
}

async function updateStatus(idea, newStatus) {
    if (!idea || idea.status === newStatus) {
        return
    }

    const oldStatus = idea.status

    idea.status = newStatus

    try {
        const response = await fetch(
            `${API_URL}/ideas/${idea.id}/`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    status: newStatus,
                }),
            }
        )

        if (!response.ok) {
            throw new Error(
                `Status update failed: ${response.status}`
            )
        }

        const updatedIdea = await response.json()

        const index = ideas.value.findIndex(
            currentIdea => currentIdea.id === updatedIdea.id
        )

        if (index !== -1) {
            ideas.value[index] = updatedIdea
        }

        if (
            selectedIdea.value?.id === updatedIdea.id
        ) {
            selectedIdea.value = updatedIdea
        }

    } catch (err) {
        console.error(err)
        idea.status = oldStatus
        error.value = "Failed to update idea status."
    }
}

async function updatePriority(idea, newPriority) {
    if (!idea || idea.priority === newPriority) {
        return
    }

    const oldPriority = idea.priority

    idea.priority = newPriority

    try {
        const response = await fetch(
            `${API_URL}/ideas/${idea.id}/`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    priority: newPriority,
                }),
            }
        )

        if (!response.ok) {
            throw new Error(
                `Priority update failed: ${response.status}`
            )
        }

        const updatedIdea = await response.json()

        const index = ideas.value.findIndex(
            currentIdea => currentIdea.id === updatedIdea.id
        )

        if (index !== -1) {
            ideas.value[index] = updatedIdea
        }

        if (
            selectedIdea.value?.id === updatedIdea.id
        ) {
            selectedIdea.value = updatedIdea
        }

    } catch (err) {
        console.error(err)
        idea.priority = oldPriority
        error.value = "Failed to update priority."
    }
}

async function archiveIdea(idea) {
    try {
        const response = await fetch(
            `${API_URL}/ideas/${idea.id}/archive/`,
            {
                method: "POST",
            }
        )

        if (!response.ok) {
            throw new Error(
                `Archive failed: ${response.status}`
            )
        }

        const updatedIdea = await response.json()

        const index = ideas.value.findIndex(
            currentIdea => currentIdea.id === updatedIdea.id
        )

        if (index !== -1) {
            ideas.value[index] = updatedIdea
        }

        selectedIdea.value = null

    } catch (err) {
        console.error(err)
        error.value = "Failed to archive idea."
    }
}

async function unarchiveIdea(idea) {
    try {
        const response = await fetch(
            `${API_URL}/ideas/${idea.id}/unarchive/`,
            { method: "POST" }
        )

        if (!response.ok) {
            throw new Error(`Unarchive failed: ${response.status}`)
        }

        const unarchivedIdea = await response.json()

        const index = ideas.value.findIndex(
            currentIdea => currentIdea.id === unarchivedIdea.id
        )

        if (index !== -1) {
            ideas.value[index] = unarchivedIdea
        } else {
            ideas.value.push(unarchivedIdea)
        }

    } catch (err) {
        console.error(err)
        error.value = "Failed to unarchive idea."
    }
}

function startDrag(idea, event) {
    draggedIdea.value = idea

    event.dataTransfer.effectAllowed = "move"

    event.dataTransfer.setData(
        "text/plain",
        String(idea.id)
    )
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

    await updateStatus(idea, status)
}


// ============================================================
// CREATE IDEA
// ============================================================

async function createIdea() {
    if (!newIdea.value.title.trim()) {
        return
    }

    try {
        const response = await fetch(
            `${API_URL}/ideas/`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    title: newIdea.value.title,
                    description: newIdea.value.description,
                    priority: newIdea.value.priority,
                    status: "NEW",
                    students: [],
                }),
            }
        )

        if (!response.ok) {
            throw new Error(
                `Create failed: ${response.status}`
            )
        }

        const createdIdea = await response.json()

        ideas.value.unshift(createdIdea)

        newIdea.value = {
            title: "",
            description: "",
            priority: "MEDIUM",
        }

        showCreateModal.value = false

    } catch (err) {
        console.error(err)
        error.value = "Failed to create idea."
    }
}


// ============================================================
// STUDENT MANAGEMENT
// ============================================================

function openCreateStudent() {
    editingStudent.value = false
    selectedStudent.value = null

    studentForm.value = {
        student_id: "",
        name: "",
        email: "",
        phone: "",
        department: "",
    }

    showStudentModal.value = true
}

function openEditStudent(student) {
    editingStudent.value = true
    selectedStudent.value = student

    studentForm.value = {
        student_id: student.student_id,
        name: student.name,
        email: student.email,
        phone: student.phone,
        department: student.department,
    }

    showStudentModal.value = true
}

function closeStudentModal() {
    showStudentModal.value = false
}

async function saveStudent() {
    const payload = {
        student_id: studentForm.value.student_id,
        name: studentForm.value.name,
        email: studentForm.value.email,
        phone: studentForm.value.phone,
        department: studentForm.value.department,
    }

    try {
        const url = editingStudent.value
            ? `${API_URL}/students/${selectedStudent.value.id}/`
            : `${API_URL}/students/`

        const response = await fetch(url, {
            method: editingStudent.value
                ? "PATCH"
                : "POST",

            headers: {
                "Content-Type": "application/json",
            },

            body: JSON.stringify(payload),
        })

        if (!response.ok) {
            const data = await response.json().catch(() => null)

            throw new Error(
                data
                    ? JSON.stringify(data)
                    : `Student request failed: ${response.status}`
            )
        }

        const savedStudent = await response.json()

        if (editingStudent.value) {
            const index = students.value.findIndex(
                student =>
                    student.id === savedStudent.id
            )

            if (index !== -1) {
                students.value[index] = savedStudent
            }

        } else {
            students.value.push(savedStudent)
        }

        showStudentModal.value = false

    } catch (err) {
        console.error(err)
        error.value = err.message
    }
}

async function deleteStudent(student) {
    const studentIdeas =
        getStudentIdeas(student)

    if (studentIdeas.length > 0) {
        error.value =
            "This student is assigned to one or more ideas. Remove them from those ideas first."

        return
    }

    if (
        !confirm(
            `Delete ${student.name}?`
        )
    ) {
        return
    }

    try {
        const response = await fetch(
            `${API_URL}/students/${student.id}/`,
            {
                method: "DELETE",
            }
        )

        if (!response.ok) {
            throw new Error(
                `Delete failed: ${response.status}`
            )
        }

        students.value =
            students.value.filter(
                current =>
                    current.id !== student.id
            )

        selectedStudent.value = null

    } catch (err) {
        console.error(err)
        error.value = "Failed to delete student."
    }
}


// ============================================================
// ASSIGN STUDENTS TO IDEA
// ============================================================

const studentPicker = ref(null)

function toggleStudentOnIdea(studentId) {
    if (!selectedIdea.value) {
        return
    }

    const currentStudents =
        [...(selectedIdea.value.students || [])]

    const exists =
        currentStudents.includes(studentId)

    const updatedStudents = exists
        ? currentStudents.filter(
              id => id !== studentId
          )
        : [...currentStudents, studentId]

    updateIdeaStudents(updatedStudents)
}

async function updateIdeaStudents(studentIds) {
    if (!selectedIdea.value) {
        return
    }

    try {
        const response = await fetch(
            `${API_URL}/ideas/${selectedIdea.value.id}/`,
            {
                method: "PATCH",

                headers: {
                    "Content-Type":
                        "application/json",
                },

                body: JSON.stringify({
                    students: studentIds,
                }),
            }
        )

        if (!response.ok) {
            throw new Error(
                `Student assignment failed: ${response.status}`
            )
        }

        const updatedIdea =
            await response.json()

        const index =
            ideas.value.findIndex(
                idea =>
                    idea.id ===
                    updatedIdea.id
            )

        if (index !== -1) {
            ideas.value[index] =
                updatedIdea
        }

        selectedIdea.value =
            updatedIdea

    } catch (err) {
        console.error(err)
        error.value =
            "Failed to update idea students."
    }
}


// ============================================================
// MEETING MANAGEMENT
// ============================================================

function openCreateMeeting(idea = null) {
    editingMeeting.value = false

    meetingForm.value = {
        id: null,
        idea: idea?.id || "",
        date: "",
        time: "",
        location: "",
        notes: "",
    }

    showMeetingModal.value = true
}

function openEditMeeting(meeting) {
    editingMeeting.value = true

    meetingForm.value = {
        id: meeting.id,
        idea: meeting.idea,
        date: meeting.date,
        time: meeting.time,
        location: meeting.location,
        notes: meeting.notes,
    }

    showMeetingModal.value = true
}

function closeMeetingModal() {
    showMeetingModal.value = false
}

async function saveMeeting() {
    if (
        !meetingForm.value.idea ||
        !meetingForm.value.date ||
        !meetingForm.value.time
    ) {
        error.value =
            "Idea, date and time are required."

        return
    }

    const payload = {
        idea: Number(meetingForm.value.idea),
        date: meetingForm.value.date,
        time: meetingForm.value.time,
        location: meetingForm.value.location,
        notes: meetingForm.value.notes,
    }

    try {
        const url = editingMeeting.value
            ? `${API_URL}/meetings/${meetingForm.value.id}/`
            : `${API_URL}/meetings/`

        const response = await fetch(url, {
            method: editingMeeting.value
                ? "PATCH"
                : "POST",

            headers: {
                "Content-Type":
                    "application/json",
            },

            body: JSON.stringify(payload),
        })

        if (!response.ok) {
            const data =
                await response.json().catch(
                    () => null
                )

            throw new Error(
                data
                    ? JSON.stringify(data)
                    : `Meeting request failed: ${response.status}`
            )
        }

        const savedMeeting =
            await response.json()

        if (editingMeeting.value) {
            const index =
                meetings.value.findIndex(
                    meeting =>
                        meeting.id ===
                        savedMeeting.id
                )

            if (index !== -1) {
                meetings.value[index] =
                    savedMeeting
            }

        } else {
            meetings.value.push(
                savedMeeting
            )
        }

        showMeetingModal.value = false

        // Refresh selected idea so its nested meetings
        // remain in sync with the API.
        if (selectedIdea.value) {
            const response =
                await fetch(
                    `${API_URL}/ideas/${selectedIdea.value.id}/`
                )

            if (response.ok) {
                selectedIdea.value =
                    await response.json()

                const index =
                    ideas.value.findIndex(
                        idea =>
                            idea.id ===
                            selectedIdea.value.id
                    )

                if (index !== -1) {
                    ideas.value[index] =
                        selectedIdea.value
                }
            }
        }

    } catch (err) {
        console.error(err)
        error.value = err.message
    }
}

async function deleteMeeting(meeting) {
    if (
        !confirm(
            "Delete this meeting?"
        )
    ) {
        return
    }

    try {
        const response = await fetch(
            `${API_URL}/meetings/${meeting.id}/`,
            {
                method: "DELETE",
            }
        )

        if (!response.ok) {
            throw new Error(
                `Delete failed: ${response.status}`
            )
        }

        meetings.value =
            meetings.value.filter(
                current =>
                    current.id !==
                    meeting.id
            )

        if (
            selectedIdea.value &&
            selectedIdea.value.meetings
        ) {
            selectedIdea.value.meetings =
                selectedIdea.value.meetings.filter(
                    current =>
                        current.id !==
                        meeting.id
                )
        }

    } catch (err) {
        console.error(err)
        error.value =
            "Failed to delete meeting."
    }
}


// ============================================================
// APPLICATION START
// ============================================================

onMounted(fetchData)
</script>


<template>
    <div :class="{ dark: darkMode }" class="h-screen">

        <main
            class="flex h-full flex-col overflow-hidden bg-slate-50 text-slate-900 dark:bg-[#0d0f14] dark:text-slate-100"
        >

            <!-- ================================================= -->
            <!-- HEADER -->
            <!-- ================================================= -->

            <header
                class="shrink-0 border-b border-slate-200 bg-white/90 px-6 py-4 backdrop-blur-xl dark:border-white/[0.06] dark:bg-[#0d0f14]/90"
            >

                <div
                    class="flex items-center justify-between"
                >

                    <div class="flex items-center gap-8">

                        <div>

                            <p
                                class="text-xs font-medium text-indigo-500"
                            >
                                Innovation Center
                            </p>

                            <h1
                                class="text-xl font-bold tracking-tight"
                            >
                                Student Ideas
                            </h1>

                        </div>


                        <!-- NAVIGATION -->

                        <nav
                            class="hidden items-center gap-1 rounded-xl bg-slate-100 p-1 dark:bg-white/[0.04] md:flex"
                        >

                            <button
                                @click="
                                    currentView =
                                        'kanban'
                                "
                                :class="
                                    currentView ===
                                    'kanban'
                                        ? 'bg-white text-slate-900 shadow-sm dark:bg-white/[0.08] dark:text-white'
                                        : 'text-slate-500 dark:text-slate-400'
                                "
                                class="rounded-lg px-4 py-2 text-xs font-medium transition"
                            >
                                Kanban
                            </button>


                            <button
                                @click="
                                    currentView =
                                        'students'
                                "
                                :class="
                                    currentView ===
                                    'students'
                                        ? 'bg-white text-slate-900 shadow-sm dark:bg-white/[0.08] dark:text-white'
                                        : 'text-slate-500 dark:text-slate-400'
                                "
                                class="rounded-lg px-4 py-2 text-xs font-medium transition"
                            >
                                Students
                                <span
                                    class="ml-1 text-[10px] opacity-50"
                                >
                                    {{ students.length }}
                                </span>
                            </button>


                            <button
                                @click="
                                    currentView =
                                        'meetings'
                                "
                                :class="
                                    currentView ===
                                    'meetings'
                                        ? 'bg-white text-slate-900 shadow-sm dark:bg-white/[0.08] dark:text-white'
                                        : 'text-slate-500 dark:text-slate-400'
                                "
                                class="rounded-lg px-4 py-2 text-xs font-medium transition"
                            >
                                Meetings
                                <span
                                    class="ml-1 text-[10px] opacity-50"
                                >
                                    {{
                                        upcomingMeetings.length
                                    }}
                                </span>
                            </button>

                        </nav>

                    </div>


                    <div class="flex items-center gap-2">

                        <button
                            @click="
                                darkMode =
                                    !darkMode
                            "
                            class="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 text-sm dark:border-white/[0.08]"
                        >
                            {{
                                darkMode
                                    ? "☀"
                                    : "☾"
                            }}
                        </button>


                        <button
                            v-if="
                                currentView ===
                                'kanban'
                            "
                            @click="
                                showCreateModal =
                                    true
                            "
                            class="rounded-xl bg-indigo-500 px-4 py-2.5 text-xs font-medium text-white shadow-lg shadow-indigo-500/20 hover:bg-indigo-600"
                        >
                            + New Idea
                        </button>


                        <button
                            v-if="
                                currentView ===
                                'students'
                            "
                            @click="
                                openCreateStudent
                            "
                            class="rounded-xl bg-indigo-500 px-4 py-2.5 text-xs font-medium text-white shadow-lg shadow-indigo-500/20 hover:bg-indigo-600"
                        >
                            + Add Student
                        </button>


                        <button
                            v-if="
                                currentView ===
                                'meetings'
                            "
                            @click="
                                openCreateMeeting()
                            "
                            class="rounded-xl bg-indigo-500 px-4 py-2.5 text-xs font-medium text-white shadow-lg shadow-indigo-500/20 hover:bg-indigo-600"
                        >
                            + Schedule Meeting
                        </button>

                    </div>

                </div>


                <!-- Mobile navigation -->

                <div
                    class="mt-4 flex gap-1 overflow-x-auto md:hidden"
                >

                    <button
                        v-for="view in [
                            'kanban',
                            'students',
                            'meetings',
                        ]"
                        :key="view"
                        @click="
                            currentView = view
                        "
                        :class="
                            currentView ===
                            view
                                ? 'bg-indigo-500 text-white'
                                : 'bg-slate-100 text-slate-500 dark:bg-white/[0.04] dark:text-slate-400'
                        "
                        class="rounded-lg px-4 py-2 text-xs font-medium capitalize"
                    >
                        {{ view }}
                    </button>

                </div>

            </header>


            <!-- ================================================= -->
            <!-- GLOBAL ERROR -->
            <!-- ================================================= -->

            <div
                v-if="error"
                class="mx-6 mt-4 shrink-0 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-xs text-red-500"
            >

                {{ error }}

                <button
                    @click="
                        error = null
                    "
                    class="ml-3 font-medium underline"
                >
                    Dismiss
                </button>

            </div>


            <!-- ================================================= -->
            <!-- LOADING -->
            <!-- ================================================= -->

            <div
                v-if="loading"
                class="flex flex-1 items-center justify-center"
            >

                <div class="text-center">

                    <div
                        class="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-slate-200 border-t-indigo-500 dark:border-white/10 dark:border-t-indigo-400"
                    />

                    <p
                        class="mt-3 text-xs text-slate-400"
                    >
                        Loading...
                    </p>

                </div>

            </div>


            <!-- ================================================= -->
            <!-- KANBAN VIEW -->
            <!-- ================================================= -->

            <template
                v-else-if="
                    currentView ===
                    'kanban'
                "
            >

                <div
                    class="shrink-0 border-b border-slate-200 px-6 py-4 dark:border-white/[0.06]"
                >

                    <div
                        class="flex flex-wrap items-center gap-3"
                    >

                        <div
                            class="relative"
                        >

                            <input
                                v-model="
                                    searchQuery
                                "
                                type="text"
                                placeholder="Search ideas..."
                                class="h-9 w-64 rounded-xl border border-slate-200 bg-white pl-3 pr-3 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
                            />

                        </div>


                        <button
                            v-for="priority in [
                                'ALL',
                                'HIGH',
                                'MEDIUM',
                                'LOW',
                            ]"
                            :key="
                                priority
                            "
                            @click="
                                selectedPriority =
                                    priority
                            "
                            :class="
                                selectedPriority ===
                                priority
                                    ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
                                    : 'bg-slate-100 text-slate-500 dark:bg-white/[0.04] dark:text-slate-400'
                            "
                            class="rounded-lg px-3 py-2 text-[10px] font-medium"
                        >
                            {{
                                priority ===
                                "ALL"
                                    ? "All"
                                    : priorityLabels[
                                          priority
                                      ]
                            }}
                        </button>


                        <button
                            @click="
                                showArchived =
                                    !showArchived
                            "
                            :class="
                                showArchived
                                    ? 'bg-indigo-500 text-white'
                                    : 'bg-slate-100 text-slate-500 dark:bg-white/[0.04] dark:text-slate-400'
                            "
                            class="ml-auto rounded-lg px-3 py-2 text-[10px] font-medium"
                        >
                            Archived
                            {{
                                archivedIdeas.length
                            }}
                        </button>

                    </div>

                </div>


                <div
                    class="min-h-0 flex-1 overflow-auto p-6"
                >

                    <div
                        class="flex min-w-max gap-5 pb-6"
                    >

                        <section
                            v-for="status in statuses"
                            :key="status"
                            @dragover.prevent
                            @drop="
                                dropIdea(status)
                            "
                            class="flex w-72 flex-col"
                        >

                            <div
                                class="mb-1 flex items-center gap-2"
                            >

                                <span
                                    class="h-2.5 w-2.5 rounded-full"
                                    :class="
                                        getStatusDotClass(
                                            status
                                        )
                                    "
                                />

                                <h2
                                    class="text-sm font-semibold"
                                >
                                    {{
                                        statusLabels[
                                            status
                                        ]
                                    }}
                                </h2>

                                <span
                                    class="rounded-md bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-500 dark:bg-white/[0.05]"
                                >
                                    {{
                                        ideasByStatus[
                                            status
                                        ].length
                                    }}
                                </span>

                            </div>


                            <p
                                class="mb-3 text-[10px] text-slate-400"
                            >
                                {{
                                    statusDescriptions[
                                        status
                                    ]
                                }}
                            </p>


                            <div class="space-y-3">

                                <article
                                    v-for="idea in ideasByStatus[
                                        status
                                    ]"
                                    :key="
                                        idea.id
                                    "
                                    draggable="true"
                                    @dragstart="
                                        startDrag(
                                            idea,
                                            $event
                                        )
                                    "
                                    @dragend="
                                        endDrag
                                    "
                                    @click="
                                        selectIdea(
                                            idea
                                        )
                                    "
                                    class="group cursor-grab rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-300 hover:shadow-lg dark:border-white/[0.07] dark:bg-[#15181f] dark:hover:border-indigo-500/40"
                                >

                                    <div
                                        class="mb-3 flex justify-between"
                                    >

                                        <span
                                            :class="
                                                getPriorityClass(
                                                    idea.priority
                                                )
                                            "
                                            class="rounded-md border px-2 py-1 text-[9px] font-semibold uppercase"
                                        >
                                            {{
                                                priorityLabels[
                                                    idea.priority
                                                ]
                                            }}
                                        </span>

                                    </div>


                                    <h3
                                        class="text-sm font-semibold"
                                    >
                                        {{
                                            idea.title
                                        }}
                                    </h3>


                                    <p
                                        class="mt-2 line-clamp-3 text-xs leading-5 text-slate-500 dark:text-slate-400"
                                    >
                                        {{
                                            idea.description
                                        }}
                                    </p>


                                    <div
                                        v-if="
                                            idea.students?.length
                                        "
                                        class="mt-4 flex items-center"
                                    >

                                        <div
                                            class="flex -space-x-2"
                                        >

                                            <div
                                                v-for="studentId in idea.students.slice(
                                                    0,
                                                    4
                                                )"
                                                :key="
                                                    studentId
                                                "
                                                class="flex h-7 w-7 items-center justify-center rounded-full border-2 border-white bg-indigo-500 text-[8px] font-semibold text-white dark:border-[#15181f]"
                                            >
                                                {{
                                                    getInitials(
                                                        getStudent(
                                                            studentId
                                                        )?.name
                                                    )
                                                }}
                                            </div>

                                        </div>


                                        <span
                                            class="ml-2 text-[10px] text-slate-400"
                                        >
                                            {{
                                                idea.students
                                                    .length
                                            }}
                                            students
                                        </span>

                                    </div>


                                  <div
                                      class="mt-4 flex items-center justify-between border-t border-slate-100 pt-3 text-[10px] text-slate-400 dark:border-white/[0.05]"
                                  >
                                      <span>
                                          📅
                                          {{
                                              getIdeaMeetings(idea).length
                                          }}
                                          meetings
                                      </span>

                                      <button
                                          v-if="showArchived"
                                          @click.stop="unarchiveIdea(idea)"
                                          class="rounded-lg px-2.5 py-1.5 text-[10px] font-medium text-indigo-500 transition hover:bg-indigo-500/10"
                                      >
                                          Unarchive
                                      </button>

                                      <span
                                          v-else
                                          class="text-indigo-500 opacity-0 transition group-hover:opacity-100"
                                      >
                                          View →
                                      </span>
                                  </div>

                                </article>


                                <div
                                    v-if="
                                        ideasByStatus[
                                            status
                                        ].length === 0
                                    "
                                    class="flex min-h-28 items-center justify-center rounded-2xl border border-dashed border-slate-200 dark:border-white/[0.07]"
                                >
                                    <span
                                        class="text-[10px] text-slate-400"
                                    >
                                        Drop ideas here
                                    </span>
                                </div>

                            </div>

                        </section>

                    </div>

                </div>

            </template>


            <!-- ================================================= -->
            <!-- STUDENTS VIEW -->
            <!-- ================================================= -->

            <template
                v-else-if="
                    currentView ===
                    'students'
                "
            >

                <div
                    class="min-h-0 flex-1 overflow-auto p-6"
                >

                    <div
                        class="mx-auto max-w-6xl"
                    >

                        <div
                            class="mb-5 flex items-center justify-between"
                        >

                            <div>

                                <h2
                                    class="text-lg font-semibold"
                                >
                                    Students
                                </h2>

                                <p
                                    class="mt-1 text-xs text-slate-400"
                                >
                                    Manage students
                                    participating in
                                    ideas.
                                </p>

                            </div>


                            <div
                                class="relative"
                            >

                                <input
                                    v-model="
                                        studentSearch
                                    "
                                    type="text"
                                    placeholder="Search students..."
                                    class="h-9 w-64 rounded-xl border border-slate-200 bg-white px-3 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
                                />

                            </div>

                        </div>


                        <div
                            class="overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-white/[0.07] dark:bg-[#15181f]"
                        >

                            <div
                                class="grid grid-cols-[2fr_1fr_2fr_1.5fr_80px] border-b border-slate-200 bg-slate-50 px-5 py-3 text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:border-white/[0.06] dark:bg-white/[0.02]"
                            >

                                <span>Name</span>
                                <span>Student ID</span>
                                <span>Email</span>
                                <span>Department</span>
                                <span></span>

                            </div>


                            <div
                                v-if="
                                    filteredStudents.length ===
                                    0
                                "
                                class="p-12 text-center"
                            >

                                <p
                                    class="text-sm text-slate-400"
                                >
                                    No students found.
                                </p>

                            </div>


                            <div
                                v-for="student in filteredStudents"
                                :key="
                                    student.id
                                "
                                @click="
                                    selectedStudent =
                                        student
                                "
                                class="grid cursor-pointer grid-cols-[2fr_1fr_2fr_1.5fr_80px] items-center border-b border-slate-100 px-5 py-4 transition last:border-0 hover:bg-slate-50 dark:border-white/[0.04] dark:hover:bg-white/[0.02]"
                            >

                                <div
                                    class="flex items-center gap-3"
                                >

                                    <div
                                        class="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-500/10 text-xs font-semibold text-indigo-500"
                                    >
                                        {{
                                            getInitials(
                                                student.name
                                            )
                                        }}
                                    </div>

                                    <div>

                                        <p
                                            class="text-xs font-medium"
                                        >
                                            {{
                                                student.name
                                            }}
                                        </p>

                                        <p
                                            class="text-[10px] text-slate-400"
                                        >
                                            {{
                                                getStudentIdeas(
                                                    student
                                                ).length
                                            }}
                                            ideas
                                        </p>

                                    </div>

                                </div>


                                <span
                                    class="text-xs text-slate-500"
                                >
                                    {{
                                        student.student_id
                                    }}
                                </span>


                                <span
                                    class="truncate text-xs text-slate-500"
                                >
                                    {{
                                        student.email
                                    }}
                                </span>


                                <span
                                    class="truncate text-xs text-slate-500"
                                >
                                    {{
                                        student.department
                                    }}
                                </span>


                                <div
                                    class="flex justify-end"
                                >

                                    <button
                                        @click.stop="
                                            openEditStudent(
                                                student
                                            )
                                        "
                                        class="rounded-lg px-2 py-1 text-[10px] text-indigo-500 hover:bg-indigo-500/10"
                                    >
                                        Edit
                                    </button>

                                </div>

                            </div>

                        </div>

                    </div>

                </div>

            </template>


            <!-- ================================================= -->
            <!-- MEETINGS VIEW -->
            <!-- ================================================= -->

            <template
                v-else-if="
                    currentView ===
                    'meetings'
                "
            >

                <div
                    class="min-h-0 flex-1 overflow-auto p-6"
                >

                    <div
                        class="mx-auto max-w-5xl"
                    >

                        <div
                            class="mb-6 flex items-center justify-between"
                        >

                            <div>

                                <h2
                                    class="text-lg font-semibold"
                                >
                                    Meetings
                                </h2>

                                <p
                                    class="mt-1 text-xs text-slate-400"
                                >
                                    Schedule and manage
                                    mentor meetings.
                                </p>

                            </div>


                            <input
                                v-model="
                                    meetingSearch
                                "
                                type="text"
                                placeholder="Search meetings..."
                                class="h-9 w-56 rounded-xl border border-slate-200 bg-white px-3 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
                            />

                        </div>


                        <!-- Upcoming -->

                        <section>

                            <h3
                                class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400"
                            >
                                Upcoming
                            </h3>


                            <div
                                v-if="
                                    upcomingMeetings.length ===
                                    0
                                "
                                class="rounded-2xl border border-dashed border-slate-200 p-10 text-center dark:border-white/[0.07]"
                            >

                                <p
                                    class="text-xs text-slate-400"
                                >
                                    No upcoming meetings.
                                </p>

                            </div>


                            <div
                                class="space-y-3"
                            >

                                <div
                                    v-for="meeting in upcomingMeetings.filter(
                                        meeting =>
                                            filteredMeetings.includes(
                                                meeting
                                            )
                                    )"
                                    :key="
                                        meeting.id
                                    "
                                    class="group rounded-2xl border border-slate-200 bg-white p-5 dark:border-white/[0.07] dark:bg-[#15181f]"
                                >

                                    <div
                                        class="flex items-start justify-between"
                                    >

                                        <div
                                            class="flex items-start gap-4"
                                        >

                                            <div
                                                :class="
                                                    isMeetingToday(
                                                        meeting
                                                    )
                                                        ? 'bg-indigo-500 text-white'
                                                        : 'bg-indigo-500/10 text-indigo-500'
                                                "
                                                class="flex h-12 w-12 flex-col items-center justify-center rounded-xl"
                                            >

                                                <span
                                                    class="text-[9px] font-medium uppercase"
                                                >
                                                    {{
                                                        new Date(
                                                            `${meeting.date}T00:00:00`
                                                        ).toLocaleDateString(
                                                            "en",
                                                            {
                                                                month: "short",
                                                            }
                                                        )
                                                    }}
                                                </span>

                                                <span
                                                    class="text-lg font-bold leading-5"
                                                >
                                                    {{
                                                        new Date(
                                                            `${meeting.date}T00:00:00`
                                                        ).getDate()
                                                    }}
                                                </span>

                                            </div>


                                            <div>

                                                <h4
                                                    class="text-sm font-semibold"
                                                >
                                                    {{
                                                        getIdea(
                                                            meeting.idea
                                                        )?.title ||
                                                        "Unknown Idea"
                                                    }}
                                                </h4>

                                                <p
                                                    class="mt-1 text-xs text-slate-400"
                                                >
                                                    {{
                                                        formatTime(
                                                            meeting.time
                                                        )
                                                    }}
                                                    <span
                                                        v-if="
                                                            meeting.location
                                                        "
                                                    >
                                                        ·
                                                        {{
                                                            meeting.location
                                                        }}
                                                    </span>
                                                </p>


                                                <div
                                                    class="mt-2 flex flex-wrap gap-1"
                                                >

                                                    <span
                                                        v-for="student in getIdeaStudents(
                                                            getIdea(
                                                                meeting.idea
                                                            )
                                                        )"
                                                        :key="
                                                            student.id
                                                        "
                                                        class="rounded-md bg-slate-100 px-2 py-1 text-[9px] text-slate-500 dark:bg-white/[0.05]"
                                                    >
                                                        {{
                                                            student.name
                                                        }}
                                                    </span>

                                                </div>

                                            </div>

                                        </div>


                                        <div
                                            class="flex gap-1 opacity-0 transition group-hover:opacity-100"
                                        >

                                            <button
                                                @click="
                                                    openEditMeeting(
                                                        meeting
                                                    )
                                                "
                                                class="rounded-lg px-2 py-1 text-[10px] text-indigo-500 hover:bg-indigo-500/10"
                                            >
                                                Edit
                                            </button>

                                            <button
                                                @click="
                                                    deleteMeeting(
                                                        meeting
                                                    )
                                                "
                                                class="rounded-lg px-2 py-1 text-[10px] text-red-500 hover:bg-red-500/10"
                                            >
                                                Delete
                                            </button>

                                        </div>

                                    </div>


                                    <p
                                        v-if="
                                            meeting.notes
                                        "
                                        class="mt-4 border-t border-slate-100 pt-3 text-xs leading-5 text-slate-500 dark:border-white/[0.05] dark:text-slate-400"
                                    >
                                        {{
                                            meeting.notes
                                        }}
                                    </p>

                                </div>

                            </div>

                        </section>


                        <!-- Past -->

                        <section
                            class="mt-10"
                        >

                            <h3
                                class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400"
                            >
                                Past Meetings
                            </h3>


                            <div
                                v-if="
                                    pastMeetings.length ===
                                    0
                                "
                                class="rounded-2xl border border-dashed border-slate-200 p-8 text-center dark:border-white/[0.07]"
                            >

                                <p
                                    class="text-xs text-slate-400"
                                >
                                    No past meetings.
                                </p>

                            </div>


                            <div
                                class="space-y-2"
                            >

                                <div
                                    v-for="meeting in pastMeetings.filter(
                                        meeting =>
                                            filteredMeetings.includes(
                                                meeting
                                            )
                                    )"
                                    :key="
                                        meeting.id
                                    "
                                    class="flex items-center justify-between rounded-xl border border-slate-200 bg-white px-4 py-3 opacity-70 dark:border-white/[0.06] dark:bg-[#15181f]"
                                >

                                    <div>

                                        <p
                                            class="text-xs font-medium"
                                        >
                                            {{
                                                getIdea(
                                                    meeting.idea
                                                )?.title ||
                                                "Unknown Idea"
                                            }}
                                        </p>

                                        <p
                                            class="mt-1 text-[10px] text-slate-400"
                                        >
                                            {{
                                                formatDate(
                                                    meeting.date
                                                )
                                            }}
                                            ·
                                            {{
                                                formatTime(
                                                    meeting.time
                                                )
                                            }}
                                        </p>

                                    </div>


                                    <div
                                        class="flex gap-1"
                                    >

                                        <button
                                            @click="
                                                openEditMeeting(
                                                    meeting
                                                )
                                            "
                                            class="rounded-lg px-2 py-1 text-[10px] text-indigo-500"
                                        >
                                            Edit
                                        </button>

                                        <button
                                            @click="
                                                deleteMeeting(
                                                    meeting
                                                )
                                            "
                                            class="rounded-lg px-2 py-1 text-[10px] text-red-500"
                                        >
                                            Delete
                                        </button>

                                    </div>

                                </div>

                            </div>

                        </section>

                    </div>

                </div>

            </template>


            <!-- ================================================= -->
            <!-- IDEA DETAILS MODAL -->
            <!-- ================================================= -->

            <div
                v-if="selectedIdea"
                class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
                @click.self="
                    closeIdea
                "
            >

                <div
                    class="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-3xl bg-white shadow-2xl dark:bg-[#15181f]"
                >

                    <div
                        class="sticky top-0 z-10 flex items-start justify-between border-b border-slate-200 bg-white/95 p-6 backdrop-blur dark:border-white/[0.06] dark:bg-[#15181f]/95"
                    >

                        <div>

                            <div
                                class="mb-3 flex gap-2"
                            >

                                <span
                                    class="rounded-md bg-slate-100 px-2 py-1 text-[10px] dark:bg-white/[0.05]"
                                >
                                    {{
                                        statusLabels[
                                            selectedIdea.status
                                        ]
                                    }}
                                </span>

                                <span
                                    :class="
                                        getPriorityClass(
                                            selectedIdea.priority
                                        )
                                    "
                                    class="rounded-md border px-2 py-1 text-[10px] uppercase"
                                >
                                    {{
                                        priorityLabels[
                                            selectedIdea.priority
                                        ]
                                    }}
                                </span>

                            </div>

                            <h2
                                class="text-xl font-semibold"
                            >
                                {{
                                    selectedIdea.title
                                }}
                            </h2>

                        </div>


                        <button
                            @click="
                                closeIdea
                            "
                            class="text-slate-400"
                        >
                            ✕
                        </button>

                    </div>


                    <div class="space-y-7 p-6">

                        <!-- Description -->

                        <section>

                            <h3
                                class="mb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400"
                            >
                                Description
                            </h3>

                            <p
                                class="text-sm leading-6 text-slate-600 dark:text-slate-300"
                            >
                                {{
                                    selectedIdea.description
                                }}
                            </p>

                        </section>


                        <!-- Students -->

                        <section>

                            <div
                                class="mb-3 flex items-center justify-between"
                            >

                                <h3
                                    class="text-[10px] font-semibold uppercase tracking-wider text-slate-400"
                                >
                                    Students
                                </h3>

                                <span
                                    class="text-[10px] text-slate-400"
                                >
                                    {{
                                        getIdeaStudents(
                                            selectedIdea
                                        ).length
                                    }}
                                    assigned
                                </span>

                            </div>


                            <div
                                class="grid gap-2 sm:grid-cols-2"
                            >

                                <button
                                    v-for="student in students"
                                    :key="
                                        student.id
                                    "
                                    @click="
                                        toggleStudentOnIdea(
                                            student.id
                                        )
                                    "
                                    :class="
                                        selectedIdea.students?.includes(
                                            student.id
                                        )
                                            ? 'border-indigo-500 bg-indigo-500/10'
                                            : 'border-slate-200 dark:border-white/[0.06]'
                                    "
                                    class="flex items-center gap-3 rounded-xl border p-3 text-left transition"
                                >

                                    <div
                                        class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-500/10 text-[10px] font-semibold text-indigo-500"
                                    >
                                        {{
                                            getInitials(
                                                student.name
                                            )
                                        }}
                                    </div>

                                    <div
                                        class="min-w-0"
                                    >

                                        <p
                                            class="truncate text-xs font-medium"
                                        >
                                            {{
                                                student.name
                                            }}
                                        </p>

                                        <p
                                            class="truncate text-[10px] text-slate-400"
                                        >
                                            {{
                                                student.student_id
                                            }}
                                        </p>

                                    </div>


                                    <span
                                        v-if="
                                            selectedIdea.students?.includes(
                                                student.id
                                            )
                                        "
                                        class="ml-auto text-indigo-500"
                                    >
                                        ✓
                                    </span>

                                </button>

                            </div>

                        </section>


                        <!-- Status -->

                        <section>

                            <h3
                                class="mb-3 text-[10px] font-semibold uppercase tracking-wider text-slate-400"
                            >
                                Status
                            </h3>

                            <div
                                class="flex flex-wrap gap-2"
                            >

                                <button
                                    v-for="status in statuses"
                                    :key="
                                        status
                                    "
                                    @click="
                                        updateStatus(
                                            selectedIdea,
                                            status
                                        )
                                    "
                                    :class="
                                        selectedIdea.status ===
                                        status
                                            ? 'bg-indigo-500 text-white'
                                            : 'border border-slate-200 dark:border-white/[0.07]'
                                    "
                                    class="rounded-lg px-3 py-2 text-xs"
                                >
                                    {{
                                        statusLabels[
                                            status
                                        ]
                                    }}
                                </button>

                            </div>

                        </section>


                        <!-- Priority -->

                        <section>

                            <h3
                                class="mb-3 text-[10px] font-semibold uppercase tracking-wider text-slate-400"
                            >
                                Priority
                            </h3>

                            <div
                                class="flex gap-2"
                            >

                                <button
                                    v-for="priority in [
                                        'LOW',
                                        'MEDIUM',
                                        'HIGH',
                                    ]"
                                    :key="
                                        priority
                                    "
                                    @click="
                                        updatePriority(
                                            selectedIdea,
                                            priority
                                        )
                                    "
                                    :class="
                                        selectedIdea.priority ===
                                        priority
                                            ? getPriorityClass(
                                                  priority
                                              )
                                            : 'border-slate-200 dark:border-white/[0.06]'
                                    "
                                    class="rounded-lg border px-3 py-2 text-xs"
                                >
                                    {{
                                        priorityLabels[
                                            priority
                                        ]
                                    }}
                                </button>

                            </div>

                        </section>


                        <!-- Meetings -->

                        <section>

                            <div
                                class="mb-3 flex items-center justify-between"
                            >

                                <h3
                                    class="text-[10px] font-semibold uppercase tracking-wider text-slate-400"
                                >
                                    Meetings
                                </h3>

                                <button
                                    @click="
                                        openCreateMeeting(
                                            selectedIdea
                                        )
                                    "
                                    class="text-xs font-medium text-indigo-500"
                                >
                                    + Schedule
                                </button>

                            </div>


                            <div
                                v-if="
                                    getIdeaMeetings(
                                        selectedIdea
                                    ).length
                                "
                                class="space-y-2"
                            >

                                <div
                                    v-for="meeting in getIdeaMeetings(
                                        selectedIdea
                                    )"
                                    :key="
                                        meeting.id
                                    "
                                    class="group rounded-xl border border-slate-200 p-4 dark:border-white/[0.06]"
                                >

                                    <div
                                        class="flex items-center justify-between"
                                    >

                                        <div>

                                            <p
                                                class="text-xs font-medium"
                                            >
                                                {{
                                                    formatDate(
                                                        meeting.date
                                                    )
                                                }}
                                                ·
                                                {{
                                                    formatTime(
                                                        meeting.time
                                                    )
                                                }}
                                            </p>

                                            <p
                                                class="mt-1 text-[10px] text-slate-400"
                                            >
                                                {{
                                                    meeting.location ||
                                                    "No location"
                                                }}
                                            </p>

                                        </div>


                                        <div
                                            class="flex gap-1 opacity-0 group-hover:opacity-100"
                                        >

                                            <button
                                                @click="
                                                    openEditMeeting(
                                                        meeting
                                                    )
                                                "
                                                class="text-[10px] text-indigo-500"
                                            >
                                                Edit
                                            </button>

                                            <button
                                                @click="
                                                    deleteMeeting(
                                                        meeting
                                                    )
                                                "
                                                class="text-[10px] text-red-500"
                                            >
                                                Delete
                                            </button>

                                        </div>

                                    </div>


                                    <p
                                        v-if="
                                            meeting.notes
                                        "
                                        class="mt-3 text-xs text-slate-500"
                                    >
                                        {{
                                            meeting.notes
                                        }}
                                    </p>

                                </div>

                            </div>


                            <div
                                v-else
                                class="rounded-xl border border-dashed border-slate-200 p-5 text-center dark:border-white/[0.06]"
                            >

                                <p
                                    class="text-xs text-slate-400"
                                >
                                    No meetings scheduled.
                                </p>

                            </div>

                        </section>

                    </div>


                    <div
                        class="flex justify-between border-t border-slate-200 p-6 dark:border-white/[0.06]"
                    >

                        <button
                            @click="
                                archiveIdea(
                                    selectedIdea
                                )
                            "
                            class="text-xs text-red-500"
                        >
                            Archive Idea
                        </button>


                        <button
                            @click="
                                closeIdea
                            "
                            class="rounded-xl bg-indigo-500 px-5 py-2.5 text-xs text-white"
                        >
                            Done
                        </button>

                    </div>

                </div>

            </div>


            <!-- ================================================= -->
            <!-- STUDENT MODAL -->
            <!-- ================================================= -->

            <div
                v-if="
                    showStudentModal
                "
                class="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
                @click.self="
                    closeStudentModal
                "
            >

                <form
                    @submit.prevent="
                        saveStudent
                    "
                    class="w-full max-w-lg rounded-3xl bg-white shadow-2xl dark:bg-[#15181f]"
                >

                    <div
                        class="flex items-center justify-between border-b border-slate-200 p-6 dark:border-white/[0.06]"
                    >

                        <div>

                            <h2
                                class="text-lg font-semibold"
                            >
                                {{
                                    editingStudent
                                        ? "Edit Student"
                                        : "Add Student"
                                }}
                            </h2>

                            <p
                                class="mt-1 text-xs text-slate-400"
                            >
                                Student information
                            </p>

                        </div>


                        <button
                            type="button"
                            @click="
                                closeStudentModal
                            "
                            class="text-slate-400"
                        >
                            ✕
                        </button>

                    </div>


                    <div class="space-y-4 p-6">

                        <div
                            class="grid gap-4 sm:grid-cols-2"
                        >

                            <label class="block">

                                <span
                                    class="mb-1.5 block text-[10px] font-medium text-slate-400"
                                >
                                    Student ID
                                </span>

                                <input
                                    v-model="
                                        studentForm.student_id
                                    "
                                    required
                                    class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
                                />

                            </label>


                            <label class="block">

                                <span
                                    class="mb-1.5 block text-[10px] font-medium text-slate-400"
                                >
                                    Name
                                </span>

                                <input
                                    v-model="
                                        studentForm.name
                                    "
                                    required
                                    class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
                                />

                            </label>

                        </div>


                        <label class="block">

                            <span
                                class="mb-1.5 block text-[10px] font-medium text-slate-400"
                            >
                                Email
                            </span>

                            <input
                                v-model="
                                    studentForm.email
                                "
                                type="email"
                                required
                                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
                            />

                        </label>


                        <div
                            class="grid gap-4 sm:grid-cols-2"
                        >

                            <label class="block">

                                <span
                                    class="mb-1.5 block text-[10px] font-medium text-slate-400"
                                >
                                    Phone
                                </span>

                                <input
                                    v-model="
                                        studentForm.phone
                                    "
                                    class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
                                />

                            </label>


                            <label class="block">

                                <span
                                    class="mb-1.5 block text-[10px] font-medium text-slate-400"
                                >
                                    Department
                                </span>

                                <input
                                    v-model="
                                        studentForm.department
                                    "
                                    required
                                    class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
                                />

                            </label>

                        </div>

                    </div>


                    <div
                        class="flex justify-between border-t border-slate-200 p-6 dark:border-white/[0.06]"
                    >

                        <button
                            v-if="
                                editingStudent
                            "
                            type="button"
                            @click="
                                deleteStudent(
                                    selectedStudent
                                )
                            "
                            class="text-xs text-red-500"
                        >
                            Delete Student
                        </button>

                        <span
                            v-else
                        ></span>


                        <div
                            class="flex gap-2"
                        >

                            <button
                                type="button"
                                @click="
                                    closeStudentModal
                                "
                                class="rounded-xl border border-slate-200 px-4 py-2.5 text-xs dark:border-white/[0.08]"
                            >
                                Cancel
                            </button>

                            <button
                                type="submit"
                                class="rounded-xl bg-indigo-500 px-5 py-2.5 text-xs text-white"
                            >
                                {{
                                    editingStudent
                                        ? "Save Changes"
                                        : "Add Student"
                                }}
                            </button>

                        </div>

                    </div>

                </form>

            </div>


            <!-- ================================================= -->
            <!-- MEETING MODAL -->
            <!-- ================================================= -->

            <div
                v-if="
                    showMeetingModal
                "
                class="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
                @click.self="
                    closeMeetingModal
                "
            >

                <form
                    @submit.prevent="
                        saveMeeting
                    "
                    class="w-full max-w-lg rounded-3xl bg-white shadow-2xl dark:bg-[#15181f]"
                >

                    <div
                        class="flex items-center justify-between border-b border-slate-200 p-6 dark:border-white/[0.06]"
                    >

                        <div>

                            <h2
                                class="text-lg font-semibold"
                            >
                                {{
                                    editingMeeting
                                        ? "Edit Meeting"
                                        : "Schedule Meeting"
                                }}
                            </h2>

                            <p
                                class="mt-1 text-xs text-slate-400"
                            >
                                Meeting details
                            </p>

                        </div>


                        <button
                            type="button"
                            @click="
                                closeMeetingModal
                            "
                            class="text-slate-400"
                        >
                            ✕
                        </button>

                    </div>


                    <div class="space-y-4 p-6">

                        <label class="block">

                            <span
                                class="mb-1.5 block text-[10px] font-medium text-slate-400"
                            >
                                Idea
                            </span>

                            <select
                                v-model="
                                    meetingForm.idea
                                "
                                required
                                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
                            >

                                <option
                                    value=""
                                    disabled
                                >
                                    Select an idea
                                </option>

                                <option
                                    v-for="idea in activeIdeas"
                                    :key="
                                        idea.id
                                    "
                                    :value="
                                        idea.id
                                    "
                                >
                                    {{
                                        idea.title
                                    }}
                                </option>

                            </select>

                        </label>


                        <div
                            class="grid gap-4 sm:grid-cols-2"
                        >

                            <label class="block">

                                <span
                                    class="mb-1.5 block text-[10px] font-medium text-slate-400"
                                >
                                    Date
                                </span>

                                <input
                                    v-model="
                                        meetingForm.date
                                    "
                                    type="date"
                                    required
                                    class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none dark:border-white/[0.08] dark:bg-white/[0.03]"
                                />

                            </label>


                            <label class="block">

                                <span
                                    class="mb-1.5 block text-[10px] font-medium text-slate-400"
                                >
                                    Time
                                </span>

                                <input
                                    v-model="
                                        meetingForm.time
                                    "
                                    type="time"
                                    required
                                    class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none dark:border-white/[0.08] dark:bg-white/[0.03]"
                                />

                            </label>

                        </div>


                        <label class="block">

                            <span
                                class="mb-1.5 block text-[10px] font-medium text-slate-400"
                            >
                                Location
                            </span>

                            <input
                                v-model="
                                    meetingForm.location
                                "
                                placeholder="e.g. Innovation Lab"
                                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
                            />

                        </label>


                        <label class="block">

                            <span
                                class="mb-1.5 block text-[10px] font-medium text-slate-400"
                            >
                                Notes
                            </span>

                            <textarea
                                v-model="
                                    meetingForm.notes
                                "
                                rows="4"
                                placeholder="Meeting agenda, discussion points, etc."
                                class="w-full resize-none rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-xs outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
                            />

                        </label>

                    </div>


                    <div
                        class="flex justify-end gap-2 border-t border-slate-200 p-6 dark:border-white/[0.06]"
                    >

                        <button
                            type="button"
                            @click="
                                closeMeetingModal
                            "
                            class="rounded-xl border border-slate-200 px-4 py-2.5 text-xs dark:border-white/[0.08]"
                        >
                            Cancel
                        </button>


                        <button
                            type="submit"
                            class="rounded-xl bg-indigo-500 px-5 py-2.5 text-xs text-white"
                        >
                            {{
                                editingMeeting
                                    ? "Save Changes"
                                    : "Schedule Meeting"
                            }}
                        </button>

                    </div>

                </form>

            </div>


            <!-- ================================================= -->
            <!-- CREATE IDEA MODAL -->
            <!-- ================================================= -->

            <div
                v-if="
                    showCreateModal
                "
                class="fixed inset-0 z-[60] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
                @click.self="
                    showCreateModal =
                        false
                "
            >

                <form
                    @submit.prevent="
                        createIdea
                    "
                    class="w-full max-w-lg rounded-3xl bg-white shadow-2xl dark:bg-[#15181f]"
                >

                    <div
                        class="flex items-center justify-between border-b border-slate-200 p-6 dark:border-white/[0.06]"
                    >

                        <h2
                            class="text-lg font-semibold"
                        >
                            New Idea
                        </h2>

                        <button
                            type="button"
                            @click="
                                showCreateModal =
                                    false
                            "
                            class="text-slate-400"
                        >
                            ✕
                        </button>

                    </div>


                    <div class="space-y-4 p-6">

                        <input
                            v-model="
                                newIdea.title
                            "
                            required
                            placeholder="Idea title"
                            class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 text-xs outline-none dark:border-white/[0.08] dark:bg-white/[0.03]"
                        />


                        <textarea
                            v-model="
                                newIdea.description
                            "
                            rows="5"
                            placeholder="Describe the idea..."
                            class="w-full resize-none rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 text-xs outline-none dark:border-white/[0.08] dark:bg-white/[0.03]"
                        />


                        <div
                            class="flex gap-2"
                        >

                            <button
                                v-for="priority in [
                                    'LOW',
                                    'MEDIUM',
                                    'HIGH',
                                ]"
                                :key="
                                    priority
                                "
                                type="button"
                                @click="
                                    newIdea.priority =
                                        priority
                                "
                                :class="
                                    newIdea.priority ===
                                    priority
                                        ? getPriorityClass(
                                              priority
                                          )
                                        : 'border-slate-200 dark:border-white/[0.06]'
                                "
                                class="flex-1 rounded-xl border px-3 py-2.5 text-xs"
                            >
                                {{
                                    priorityLabels[
                                        priority
                                    ]
                                }}
                            </button>

                        </div>

                    </div>


                    <div
                        class="flex justify-end gap-2 border-t border-slate-200 p-6 dark:border-white/[0.06]"
                    >

                        <button
                            type="button"
                            @click="
                                showCreateModal =
                                    false
                            "
                            class="rounded-xl border border-slate-200 px-4 py-2.5 text-xs dark:border-white/[0.08]"
                        >
                            Cancel
                        </button>

                        <button
                            type="submit"
                            class="rounded-xl bg-indigo-500 px-5 py-2.5 text-xs text-white"
                        >
                            Create Idea
                        </button>

                    </div>

                </form>

            </div>

        </main>

    </div>
</template>
```
