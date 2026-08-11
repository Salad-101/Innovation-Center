```vue
<script setup>
import { computed, onMounted, ref } from "vue"

// ============================================================
// Configuration
// ============================================================

const API_URL = "http://127.0.0.1:8000/api"


// ============================================================
// State
// ============================================================

const ideas = ref([])
const students = ref([])

const loading = ref(true)
const error = ref(null)

const selectedIdea = ref(null)

const searchQuery = ref("")
const selectedPriority = ref("ALL")

const darkMode = ref(true)
const showArchived = ref(false)

const showCreateModal = ref(false)

const newIdea = ref({
    title: "",
    description: "",
    priority: "MEDIUM",
})

const draggedIdea = ref(null)


// ============================================================
// Kanban statuses
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
// Computed
// ============================================================

const activeIdeas = computed(() => {
    return ideas.value.filter(
        idea => !idea.is_archived
    )
})

const archivedIdeas = computed(() => {
    return ideas.value.filter(
        idea => idea.is_archived
    )
})

const filteredIdeas = computed(() => {
    let result = showArchived.value
        ? archivedIdeas.value
        : activeIdeas.value

    // Search
    if (searchQuery.value.trim()) {
        const query =
            searchQuery.value
                .trim()
                .toLowerCase()

        result = result.filter(idea => {
            return (
                idea.title
                    ?.toLowerCase()
                    .includes(query) ||

                idea.description
                    ?.toLowerCase()
                    .includes(query)
            )
        })
    }

    // Priority
    if (selectedPriority.value !== "ALL") {
        result = result.filter(
            idea =>
                idea.priority ===
                selectedPriority.value
        )
    }

    return result
})

const ideasByStatus = computed(() => {
    const groups = {}

    for (const status of statuses) {
        groups[status] =
            filteredIdeas.value.filter(
                idea =>
                    idea.status === status
            )
    }

    return groups
})

const totalIdeas = computed(() => {
    return activeIdeas.value.length
})

const reviewCount = computed(() => {
    return activeIdeas.value.filter(
        idea => idea.status === "REVIEW"
    ).length
})

const refinementCount = computed(() => {
    return activeIdeas.value.filter(
        idea => idea.status === "REFINEMENT"
    ).length
})

const approvedCount = computed(() => {
    return activeIdeas.value.filter(
        idea => idea.status === "APPROVED"
    ).length
})

const scheduledMeetingCount = computed(() => {
    return activeIdeas.value.filter(
        idea =>
            idea.meetings &&
            idea.meetings.length > 0
    ).length
})


// ============================================================
// API - Fetch
// ============================================================

async function fetchData() {
    loading.value = true
    error.value = null

    try {
        const [
            ideasResponse,
            studentsResponse,
        ] = await Promise.all([
            fetch(`${API_URL}/ideas/`),
            fetch(`${API_URL}/students/`),
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

        ideas.value =
            await ideasResponse.json()

        students.value =
            await studentsResponse.json()

    } catch (err) {
        console.error(err)

        error.value =
            err.message ||
            "Failed to load application data."

    } finally {
        loading.value = false
    }
}


// ============================================================
// Student helpers
// ============================================================

function getStudent(studentId) {
    return students.value.find(
        student =>
            student.id === studentId
    )
}

function getIdeaStudents(idea) {
    if (!idea?.students) {
        return []
    }

    return idea.students
        .map(studentId =>
            getStudent(studentId)
        )
        .filter(Boolean)
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
// Formatting helpers
// ============================================================

function formatDate(date) {
    if (!date) {
        return ""
    }

    return new Intl.DateTimeFormat(
        "en",
        {
            month: "short",
            day: "numeric",
            year: "numeric",
        }
    ).format(new Date(date))
}

function formatTime(time) {
    if (!time) {
        return ""
    }

    const [hours, minutes] =
        time.split(":")

    const date =
        new Date()

    date.setHours(
        Number(hours),
        Number(minutes)
    )

    return new Intl.DateTimeFormat(
        "en",
        {
            hour: "numeric",
            minute: "2-digit",
        }
    ).format(date)
}


// ============================================================
// UI helpers
// ============================================================

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
// Idea details
// ============================================================

function selectIdea(idea) {
    selectedIdea.value = idea
}

function closeIdea() {
    selectedIdea.value = null
}


// ============================================================
// Update status
// ============================================================

async function updateStatus(
    idea,
    newStatus
) {
    if (!idea) {
        return
    }

    const oldStatus =
        idea.status

    if (oldStatus === newStatus) {
        return
    }

    // Optimistic update
    idea.status = newStatus

    try {
        const response =
            await fetch(
                `${API_URL}/ideas/${idea.id}/`,
                {
                    method: "PATCH",

                    headers: {
                        "Content-Type":
                            "application/json",
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

        const updatedIdea =
            await response.json()

        const index =
            ideas.value.findIndex(
                currentIdea =>
                    currentIdea.id ===
                    updatedIdea.id
            )

        if (index !== -1) {
            ideas.value[index] =
                updatedIdea
        }

        if (
            selectedIdea.value &&
            selectedIdea.value.id ===
                updatedIdea.id
        ) {
            selectedIdea.value =
                updatedIdea
        }

    } catch (err) {
        console.error(err)

        idea.status = oldStatus

        error.value =
            "Failed to update the idea status."
    }
}


// ============================================================
// Update priority
// ============================================================

async function updatePriority(
    idea,
    newPriority
) {
    if (!idea) {
        return
    }

    const oldPriority =
        idea.priority

    if (
        oldPriority ===
        newPriority
    ) {
        return
    }

    // Optimistic update
    idea.priority = newPriority

    try {
        const response =
            await fetch(
                `${API_URL}/ideas/${idea.id}/`,
                {
                    method: "PATCH",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({
                        priority:
                            newPriority,
                    }),
                }
            )

        if (!response.ok) {
            throw new Error(
                `Priority update failed: ${response.status}`
            )
        }

        const updatedIdea =
            await response.json()

        const index =
            ideas.value.findIndex(
                currentIdea =>
                    currentIdea.id ===
                    updatedIdea.id
            )

        if (index !== -1) {
            ideas.value[index] =
                updatedIdea
        }

        if (
            selectedIdea.value &&
            selectedIdea.value.id ===
                updatedIdea.id
        ) {
            selectedIdea.value =
                updatedIdea
        }

    } catch (err) {
        console.error(err)

        idea.priority =
            oldPriority

        error.value =
            "Failed to update priority."
    }
}


// ============================================================
// Archive
// ============================================================

async function archiveIdea(idea) {
    if (!idea) {
        return
    }

    try {
        const response =
            await fetch(
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

        const updatedIdea =
            await response.json()

        const index =
            ideas.value.findIndex(
                currentIdea =>
                    currentIdea.id ===
                    updatedIdea.id
            )

        if (index !== -1) {
            ideas.value[index] =
                updatedIdea
        }

        selectedIdea.value =
            null

    } catch (err) {
        console.error(err)

        error.value =
            "Failed to archive the idea."
    }
}


// ============================================================
// Drag & Drop
// ============================================================

function startDrag(
    idea,
    event
) {
    draggedIdea.value = idea

    event.dataTransfer.effectAllowed =
        "move"

    event.dataTransfer.setData(
        "text/plain",
        String(idea.id)
    )
}

function endDrag() {
    draggedIdea.value =
        null
}

async function dropIdea(
    newStatus
) {
    if (!draggedIdea.value) {
        return
    }

    const idea =
        draggedIdea.value

    draggedIdea.value =
        null

    await updateStatus(
        idea,
        newStatus
    )
}


// ============================================================
// Create Idea
// ============================================================

async function createIdea() {
    if (
        !newIdea.value.title.trim()
    ) {
        return
    }

    try {
        const response =
            await fetch(
                `${API_URL}/ideas/`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({
                        title:
                            newIdea.value
                                .title,

                        description:
                            newIdea.value
                                .description,

                        priority:
                            newIdea.value
                                .priority,

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

        const createdIdea =
            await response.json()

        ideas.value.unshift(
            createdIdea
        )

        newIdea.value = {
            title: "",
            description: "",
            priority: "MEDIUM",
        }

        showCreateModal.value =
            false

    } catch (err) {
        console.error(err)

        error.value =
            "Failed to create the idea."
    }
}


// ============================================================
// Start application
// ============================================================

onMounted(() => {
    fetchData()
})
</script>


<template>
    <div
        :class="darkMode ? 'dark' : ''"
        class="h-screen overflow-hidden"
    >

        <main
            class="flex h-full flex-col bg-slate-50 text-slate-900 transition-colors duration-300 dark:bg-[#0d0f14] dark:text-slate-100"
        >

            <!-- ================================================= -->
            <!-- HEADER -->
            <!-- ================================================= -->

            <header
                class="shrink-0 border-b border-slate-200 bg-white/90 px-6 py-5 backdrop-blur-xl dark:border-white/[0.06] dark:bg-[#0d0f14]/90"
            >

                <div
                    class="flex flex-wrap items-center justify-between gap-4"
                >

                    <div>

                        <p
                            class="text-xs font-medium text-indigo-500 dark:text-indigo-400"
                        >
                            Innovation Center
                        </p>

                        <h1
                            class="mt-1 text-2xl font-bold tracking-tight"
                        >
                            Student Ideas
                        </h1>

                        <p
                            class="mt-1 text-sm text-slate-500 dark:text-slate-400"
                        >
                            Manage and track student
                            startup ideas
                        </p>

                    </div>


                    <div
                        class="flex items-center gap-2"
                    >

                        <!-- Search -->

                        <div
                            class="relative hidden md:block"
                        >

                            <svg
                                class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <circle
                                    cx="11"
                                    cy="11"
                                    r="7"
                                    stroke-width="1.8"
                                />

                                <path
                                    d="m20 20-4-4"
                                    stroke-linecap="round"
                                    stroke-width="1.8"
                                />
                            </svg>

                            <input
                                v-model="
                                    searchQuery
                                "
                                type="text"
                                placeholder="Search ideas..."
                                class="h-10 w-56 rounded-xl border border-slate-200 bg-slate-50 pl-9 pr-3 text-sm outline-none transition focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
                            />

                        </div>


                        <!-- Dark mode -->

                        <button
                            @click="
                                darkMode =
                                    !darkMode
                            "
                            class="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-500 transition hover:bg-slate-50 dark:border-white/[0.08] dark:bg-white/[0.03]"
                            title="Toggle dark mode"
                        >
                            {{
                                darkMode
                                    ? "☀"
                                    : "☾"
                            }}
                        </button>


                        <!-- New idea -->

                        <button
                            @click="
                                showCreateModal =
                                    true
                            "
                            class="flex h-10 items-center gap-2 rounded-xl bg-indigo-500 px-4 text-sm font-medium text-white shadow-lg shadow-indigo-500/20 transition hover:bg-indigo-600 active:scale-[0.98]"
                        >
                            <span
                                class="text-lg leading-none"
                            >
                                +
                            </span>

                            New Idea
                        </button>

                    </div>

                </div>


                <!-- ================================================= -->
                <!-- STATS -->
                <!-- ================================================= -->

                <div
                    class="mt-5 grid grid-cols-2 gap-3 lg:grid-cols-5"
                >

                    <div
                        class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-white/[0.06] dark:bg-white/[0.02]"
                    >
                        <p
                            class="text-[11px] text-slate-400"
                        >
                            Active Ideas
                        </p>

                        <p
                            class="mt-1 text-xl font-semibold"
                        >
                            {{ totalIdeas }}
                        </p>
                    </div>


                    <div
                        class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-white/[0.06] dark:bg-white/[0.02]"
                    >
                        <p
                            class="text-[11px] text-slate-400"
                        >
                            Meetings
                        </p>

                        <p
                            class="mt-1 text-xl font-semibold"
                        >
                            {{
                                scheduledMeetingCount
                            }}
                        </p>
                    </div>


                    <div
                        class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-white/[0.06] dark:bg-white/[0.02]"
                    >
                        <p
                            class="text-[11px] text-slate-400"
                        >
                            Under Review
                        </p>

                        <p
                            class="mt-1 text-xl font-semibold"
                        >
                            {{ reviewCount }}
                        </p>
                    </div>


                    <div
                        class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-white/[0.06] dark:bg-white/[0.02]"
                    >
                        <p
                            class="text-[11px] text-slate-400"
                        >
                            Refinement
                        </p>

                        <p
                            class="mt-1 text-xl font-semibold"
                        >
                            {{
                                refinementCount
                            }}
                        </p>
                    </div>


                    <div
                        class="rounded-xl border border-slate-200 bg-slate-50 p-3 dark:border-white/[0.06] dark:bg-white/[0.02]"
                    >
                        <p
                            class="text-[11px] text-slate-400"
                        >
                            Approved
                        </p>

                        <p
                            class="mt-1 text-xl font-semibold"
                        >
                            {{ approvedCount }}
                        </p>
                    </div>

                </div>


                <!-- ================================================= -->
                <!-- FILTERS -->
                <!-- ================================================= -->

                <div
                    class="mt-4 flex items-center gap-2"
                >

                    <span
                        class="mr-1 text-xs text-slate-400"
                    >
                        Priority
                    </span>

                    <button
                        v-for="priority in [
                            'ALL',
                            'HIGH',
                            'MEDIUM',
                            'LOW',
                        ]"
                        :key="priority"
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
                        class="rounded-lg px-3 py-1.5 text-xs font-medium transition"
                    >
                        {{
                            priority === "ALL"
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
                        class="ml-auto rounded-lg px-3 py-1.5 text-xs font-medium transition"
                    >
                        Archived
                        {{
                            archivedIdeas.length
                        }}
                    </button>

                </div>

            </header>


            <!-- ================================================= -->
            <!-- ERROR -->
            <!-- ================================================= -->

            <div
                v-if="error"
                class="mx-6 mt-5 rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-500"
            >

                {{ error }}

                <button
                    @click="fetchData"
                    class="ml-2 font-medium underline"
                >
                    Retry
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
                        Loading ideas...
                    </p>

                </div>

            </div>


            <!-- ================================================= -->
            <!-- BOARD -->
            <!-- ================================================= -->

            <div
                v-else
                class="min-h-0 flex-1 overflow-x-auto overflow-y-auto p-6"
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

                        <!-- Column header -->

                        <div
                            class="mb-3 flex items-center justify-between"
                        >

                            <div
                                class="flex items-center gap-2"
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
                                    class="rounded-md bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-500 dark:bg-white/[0.05] dark:text-slate-400"
                                >
                                    {{
                                        ideasByStatus[
                                            status
                                        ].length
                                    }}
                                </span>

                            </div>

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


                        <!-- Cards -->

                        <div
                            class="min-h-32 space-y-3"
                        >

                            <article
                                v-for="idea in ideasByStatus[
                                    status
                                ]"
                                :key="idea.id"
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
                                class="group cursor-grab rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-indigo-300 hover:shadow-lg dark:border-white/[0.07] dark:bg-[#15181f] dark:hover:border-indigo-500/40 active:cursor-grabbing"
                            >

                                <!-- Priority -->

                                <div
                                    class="mb-3 flex items-center justify-between"
                                >

                                    <span
                                        :class="
                                            getPriorityClass(
                                                idea.priority
                                            )
                                        "
                                        class="rounded-md border px-2 py-1 text-[9px] font-semibold uppercase tracking-wide"
                                    >
                                        {{
                                            priorityLabels[
                                                idea.priority
                                            ]
                                        }}
                                    </span>

                                    <span
                                        class="text-[10px] text-slate-400"
                                    >
                                        #{{ idea.id }}
                                    </span>

                                </div>


                                <!-- Title -->

                                <h3
                                    class="text-sm font-semibold leading-5"
                                >
                                    {{ idea.title }}
                                </h3>


                                <!-- Description -->

                                <p
                                    class="mt-2 line-clamp-3 text-xs leading-5 text-slate-500 dark:text-slate-400"
                                >
                                    {{
                                        idea.description
                                    }}
                                </p>


                                <!-- Students -->

                                <div
                                    v-if="
                                        idea.students &&
                                        idea.students.length
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
                                        {{
                                            idea.students
                                                .length ===
                                            1
                                                ? "student"
                                                : "students"
                                        }}
                                    </span>

                                </div>


                                <!-- Footer -->

                                <div
                                    class="mt-4 flex items-center justify-between border-t border-slate-100 pt-3 dark:border-white/[0.05]"
                                >

                                    <span
                                        v-if="
                                            idea.meetings &&
                                            idea.meetings
                                                .length
                                        "
                                        class="text-[10px] text-slate-400"
                                    >
                                        📅
                                        {{
                                            idea.meetings
                                                .length
                                        }}
                                        {{
                                            idea.meetings
                                                .length ===
                                            1
                                                ? "meeting"
                                                : "meetings"
                                        }}
                                    </span>

                                    <span
                                        v-else
                                        class="text-[10px] text-slate-400"
                                    >
                                        No meetings
                                    </span>


                                    <span
                                        class="text-[10px] font-medium text-indigo-500 opacity-0 transition group-hover:opacity-100"
                                    >
                                        View →
                                    </span>

                                </div>

                            </article>


                            <!-- Empty column -->

                            <div
                                v-if="
                                    ideasByStatus[
                                        status
                                    ].length === 0
                                "
                                class="flex min-h-32 items-center justify-center rounded-2xl border border-dashed border-slate-200 dark:border-white/[0.07]"
                            >

                                <p
                                    class="text-[10px] text-slate-400"
                                >
                                    Drop ideas here
                                </p>

                            </div>

                        </div>

                    </section>

                </div>

            </div>


            <!-- ================================================= -->
            <!-- IDEA DETAILS MODAL -->
            <!-- ================================================= -->

            <div
                v-if="selectedIdea"
                class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
                @click.self="closeIdea"
            >

                <div
                    class="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-3xl border border-slate-200 bg-white shadow-2xl dark:border-white/[0.08] dark:bg-[#15181f]"
                >

                    <!-- Modal header -->

                    <div
                        class="sticky top-0 z-10 border-b border-slate-200 bg-white/95 p-6 backdrop-blur-xl dark:border-white/[0.06] dark:bg-[#15181f]/95"
                    >

                        <div
                            class="flex items-start justify-between gap-4"
                        >

                            <div>

                                <div
                                    class="mb-3 flex flex-wrap items-center gap-2"
                                >

                                    <span
                                        class="flex items-center gap-1.5 rounded-md bg-slate-100 px-2 py-1 text-[10px] font-medium text-slate-500 dark:bg-white/[0.05] dark:text-slate-400"
                                    >

                                        <span
                                            class="h-1.5 w-1.5 rounded-full"
                                            :class="
                                                getStatusDotClass(
                                                    selectedIdea.status
                                                )
                                            "
                                        />

                                        {{
                                            statusLabels[
                                                selectedIdea
                                                    .status
                                            ]
                                        }}

                                    </span>


                                    <span
                                        :class="
                                            getPriorityClass(
                                                selectedIdea.priority
                                            )
                                        "
                                        class="rounded-md border px-2 py-1 text-[10px] font-semibold uppercase"
                                    >
                                        {{
                                            priorityLabels[
                                                selectedIdea
                                                    .priority
                                            ]
                                        }}
                                    </span>

                                </div>


                                <h2
                                    class="text-xl font-semibold tracking-tight"
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
                                class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-slate-400 hover:bg-slate-100 dark:hover:bg-white/[0.06]"
                            >
                                ✕
                            </button>

                        </div>

                    </div>


                    <div class="space-y-7 p-6">

                        <!-- Description -->

                        <section>

                            <h3
                                class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400"
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
                                    class="text-xs font-semibold uppercase tracking-wider text-slate-400"
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
                                    students
                                </span>

                            </div>


                            <div
                                v-if="
                                    getIdeaStudents(
                                        selectedIdea
                                    ).length
                                "
                                class="grid gap-2 sm:grid-cols-2"
                            >

                                <div
                                    v-for="student in getIdeaStudents(
                                        selectedIdea
                                    )"
                                    :key="
                                        student.id
                                    "
                                    class="flex items-center gap-3 rounded-xl border border-slate-200 p-3 dark:border-white/[0.06]"
                                >

                                    <div
                                        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-indigo-500/10 text-xs font-semibold text-indigo-500"
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

                                        <p
                                            class="truncate text-[10px] text-slate-400"
                                        >
                                            {{
                                                student.department
                                            }}
                                        </p>

                                    </div>

                                </div>

                            </div>


                            <div
                                v-else
                                class="rounded-xl border border-dashed border-slate-200 p-5 text-center dark:border-white/[0.06]"
                            >
                                <p
                                    class="text-xs text-slate-400"
                                >
                                    No students assigned.
                                </p>
                            </div>

                        </section>


                        <!-- Status -->

                        <section>

                            <h3
                                class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400"
                            >
                                Status
                            </h3>

                            <div
                                class="flex flex-wrap gap-2"
                            >

                                <button
                                    v-for="status in statuses"
                                    :key="status"
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
                                            : 'border border-slate-200 text-slate-500 dark:border-white/[0.07] dark:text-slate-400'
                                    "
                                    class="rounded-lg px-3 py-2 text-xs font-medium transition"
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
                                class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400"
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
                                            : 'border-slate-200 text-slate-400 dark:border-white/[0.06]'
                                    "
                                    class="rounded-lg border px-3 py-2 text-xs font-medium"
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
                                    class="text-xs font-semibold uppercase tracking-wider text-slate-400"
                                >
                                    Meetings
                                </h3>

                                <button
                                    class="text-xs font-medium text-indigo-500 hover:text-indigo-400"
                                >
                                    + Schedule Meeting
                                </button>

                            </div>


                            <div
                                v-if="
                                    selectedIdea.meetings &&
                                    selectedIdea
                                        .meetings.length
                                "
                                class="space-y-2"
                            >

                                <div
                                    v-for="meeting in selectedIdea.meetings"
                                    :key="
                                        meeting.id
                                    "
                                    class="rounded-xl border border-slate-200 p-4 dark:border-white/[0.06]"
                                >

                                    <div
                                        class="flex items-center justify-between"
                                    >

                                        <p
                                            class="text-sm font-medium"
                                        >
                                            {{
                                                formatDate(
                                                    meeting.date
                                                )
                                            }}
                                        </p>

                                        <p
                                            class="text-xs text-slate-400"
                                        >
                                            {{
                                                formatTime(
                                                    meeting.time
                                                )
                                            }}
                                        </p>

                                    </div>


                                    <p
                                        class="mt-1 text-xs text-slate-400"
                                    >
                                        {{
                                            meeting.location ||
                                            "No location specified"
                                        }}
                                    </p>


                                    <p
                                        v-if="
                                            meeting.notes
                                        "
                                        class="mt-3 text-xs leading-5 text-slate-500 dark:text-slate-400"
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
                                    No meetings scheduled
                                    for this idea.
                                </p>

                            </div>

                        </section>

                    </div>


                    <!-- Modal footer -->

                    <div
                        class="flex items-center justify-between border-t border-slate-200 p-6 dark:border-white/[0.06]"
                    >

                        <button
                            @click="
                                archiveIdea(
                                    selectedIdea
                                )
                            "
                            class="text-xs font-medium text-red-500 hover:text-red-400"
                        >
                            Archive Idea
                        </button>


                        <button
                            @click="
                                closeIdea
                            "
                            class="rounded-xl bg-indigo-500 px-5 py-2.5 text-xs font-medium text-white transition hover:bg-indigo-600"
                        >
                            Done
                        </button>

                    </div>

                </div>

            </div>


            <!-- ================================================= -->
            <!-- CREATE IDEA MODAL -->
            <!-- ================================================= -->

            <div
                v-if="showCreateModal"
                class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
                @click.self="
                    showCreateModal =
                        false
                "
            >

                <div
                    class="w-full max-w-lg rounded-3xl border border-slate-200 bg-white shadow-2xl dark:border-white/[0.08] dark:bg-[#15181f]"
                >

                    <div
                        class="flex items-center justify-between border-b border-slate-200 p-6 dark:border-white/[0.06]"
                    >

                        <div>

                            <h2
                                class="text-lg font-semibold"
                            >
                                New Student Idea
                            </h2>

                            <p
                                class="mt-1 text-xs text-slate-400"
                            >
                                Add an idea to the
                                Innovation Center.
                            </p>

                        </div>


                        <button
                            @click="
                                showCreateModal =
                                    false
                            "
                            class="text-slate-400"
                        >
                            ✕
                        </button>

                    </div>


                    <form
                        @submit.prevent="
                            createIdea
                        "
                        class="space-y-5 p-6"
                    >

                        <!-- Title -->

                        <div>

                            <label
                                class="mb-2 block text-xs font-medium"
                            >
                                Idea Title
                            </label>

                            <input
                                v-model="
                                    newIdea.title
                                "
                                type="text"
                                required
                                placeholder="e.g. Smart Campus Navigation"
                                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 text-sm outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
                            />

                        </div>


                        <!-- Description -->

                        <div>

                            <label
                                class="mb-2 block text-xs font-medium"
                            >
                                Description
                            </label>

                            <textarea
                                v-model="
                                    newIdea.description
                                "
                                rows="5"
                                placeholder="Describe the student's idea..."
                                class="w-full resize-none rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 text-sm outline-none focus:border-indigo-400 dark:border-white/[0.08] dark:bg-white/[0.03]"
                            />

                        </div>


                        <!-- Priority -->

                        <div>

                            <label
                                class="mb-2 block text-xs font-medium"
                            >
                                Priority
                            </label>

                            <div
                                class="grid grid-cols-3 gap-2"
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
                                            : 'border-slate-200 text-slate-400 dark:border-white/[0.06]'
                                    "
                                    class="rounded-xl border px-3 py-2.5 text-xs font-medium"
                                >
                                    {{
                                        priorityLabels[
                                            priority
                                        ]
                                    }}
                                </button>

                            </div>

                        </div>


                        <!-- Buttons -->

                        <div
                            class="flex justify-end gap-2 border-t border-slate-200 pt-5 dark:border-white/[0.06]"
                        >

                            <button
                                type="button"
                                @click="
                                    showCreateModal =
                                        false
                                "
                                class="rounded-xl border border-slate-200 px-4 py-2.5 text-xs font-medium dark:border-white/[0.08]"
                            >
                                Cancel
                            </button>


                            <button
                                type="submit"
                                class="rounded-xl bg-indigo-500 px-5 py-2.5 text-xs font-medium text-white shadow-lg shadow-indigo-500/20 transition hover:bg-indigo-600"
                            >
                                Create Idea
                            </button>

                        </div>

                    </form>

                </div>

            </div>

        </main>

    </div>
</template>
```
