import { computed, ref } from "vue"
import { defineStore } from "pinia"

const API_URL = "http://127.0.0.1:8000/api"

export const useIdeasStore = defineStore("ideas", () => {

    // ============================================================
    // STATE
    // ============================================================

    const ideas = ref([])
    const students = ref([])
    const meetings = ref([])

    const loading = ref(true)
    const error = ref(null)


    // ============================================================
    // COMPUTED
    // ============================================================

    const activeIdeas = computed(() =>
        ideas.value.filter(idea => !idea.is_archived)
    )

    const archivedIdeas = computed(() =>
        ideas.value.filter(idea => idea.is_archived)
    )


    // ============================================================
    // FETCH
    // ============================================================

    async function fetchData() {
        loading.value = true
        error.value = null

        try {
            const [ideasResponse, studentsResponse, meetingsResponse] =
                await Promise.all([
                    fetch(`${API_URL}/ideas/`),
                    fetch(`${API_URL}/students/`),
                    fetch(`${API_URL}/meetings/`),
                ])

            if (!ideasResponse.ok) {
                throw new Error(`Ideas request failed: ${ideasResponse.status}`)
            }

            if (!studentsResponse.ok) {
                throw new Error(`Students request failed: ${studentsResponse.status}`)
            }

            if (!meetingsResponse.ok) {
                throw new Error(`Meetings request failed: ${meetingsResponse.status}`)
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

        return idea.students.map(id => getStudent(id)).filter(Boolean)
    }

    function getIdeaMeetings(idea) {
        if (!idea) {
            return []
        }

        return meetings.value.filter(meeting => meeting.idea === idea.id)
    }

    function getStudentIdeas(student) {
        if (!student) {
            return []
        }

        return ideas.value.filter(idea => idea.students?.includes(student.id))
    }


    // ============================================================
    // IDEA MUTATIONS
    // ============================================================

    async function updateStatus(idea, newStatus) {
        if (!idea || idea.status === newStatus) {
            return
        }

        const oldStatus = idea.status
        idea.status = newStatus

        try {
            const response = await fetch(`${API_URL}/ideas/${idea.id}/`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ status: newStatus }),
            })

            if (!response.ok) {
                throw new Error(`Status update failed: ${response.status}`)
            }

            const updatedIdea = await response.json()
            const index = ideas.value.findIndex(current => current.id === updatedIdea.id)
            if (index !== -1) {
                ideas.value[index] = updatedIdea
            }

            return updatedIdea

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
            const response = await fetch(`${API_URL}/ideas/${idea.id}/`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ priority: newPriority }),
            })

            if (!response.ok) {
                throw new Error(`Priority update failed: ${response.status}`)
            }

            const updatedIdea = await response.json()
            const index = ideas.value.findIndex(current => current.id === updatedIdea.id)
            if (index !== -1) {
                ideas.value[index] = updatedIdea
            }

            return updatedIdea

        } catch (err) {
            console.error(err)
            idea.priority = oldPriority
            error.value = "Failed to update priority."
        }
    }

    async function archiveIdea(idea) {
        try {
            const response = await fetch(`${API_URL}/ideas/${idea.id}/archive/`, {
                method: "POST",
            })

            if (!response.ok) {
                throw new Error(`Archive failed: ${response.status}`)
            }

            const updatedIdea = await response.json()
            const index = ideas.value.findIndex(current => current.id === updatedIdea.id)
            if (index !== -1) {
                ideas.value[index] = updatedIdea
            }

            return updatedIdea

        } catch (err) {
            console.error(err)
            error.value = "Failed to archive idea."
        }
    }

    async function unarchiveIdea(idea) {
        try {
            const response = await fetch(`${API_URL}/ideas/${idea.id}/unarchive/`, {
                method: "POST",
            })

            if (!response.ok) {
                throw new Error(`Unarchive failed: ${response.status}`)
            }

            const unarchivedIdea = await response.json()

            // The idea already exists in `ideas` (just flagged is_archived) —
            // replace it in place rather than pushing a duplicate entry.
            const index = ideas.value.findIndex(current => current.id === unarchivedIdea.id)

            if (index !== -1) {
                ideas.value[index] = unarchivedIdea
            } else {
                ideas.value.push(unarchivedIdea)
            }

            return unarchivedIdea

        } catch (err) {
            console.error(err)
            error.value = "Failed to unarchive idea."
        }
    }

    async function createIdea({ title, description, priority }) {
        try {
            const response = await fetch(`${API_URL}/ideas/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    title,
                    description,
                    priority,
                    status: "NEW",
                    students: [],
                }),
            })

            if (!response.ok) {
                throw new Error(`Create failed: ${response.status}`)
            }

            const createdIdea = await response.json()
            ideas.value.unshift(createdIdea)

            return createdIdea

        } catch (err) {
            console.error(err)
            error.value = "Failed to create idea."
        }
    }

    async function updateIdeaStudents(idea, studentIds) {
        if (!idea) {
            return
        }

        try {
            const response = await fetch(`${API_URL}/ideas/${idea.id}/`, {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ students: studentIds }),
            })

            if (!response.ok) {
                throw new Error(`Student assignment failed: ${response.status}`)
            }

            const updatedIdea = await response.json()
            const index = ideas.value.findIndex(current => current.id === updatedIdea.id)
            if (index !== -1) {
                ideas.value[index] = updatedIdea
            }

            return updatedIdea

        } catch (err) {
            console.error(err)
            error.value = "Failed to update idea students."
        }
    }


    // ============================================================
    // STUDENT MUTATIONS
    // ============================================================

    async function saveStudent(payload, existingId = null) {
        try {
            const url = existingId
                ? `${API_URL}/students/${existingId}/`
                : `${API_URL}/students/`

            const response = await fetch(url, {
                method: existingId ? "PATCH" : "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            })

            if (!response.ok) {
                const data = await response.json().catch(() => null)
                throw new Error(data ? JSON.stringify(data) : `Student request failed: ${response.status}`)
            }

            const savedStudent = await response.json()

            if (existingId) {
                const index = students.value.findIndex(student => student.id === savedStudent.id)
                if (index !== -1) {
                    students.value[index] = savedStudent
                }
            } else {
                students.value.push(savedStudent)
            }

            return savedStudent

        } catch (err) {
            console.error(err)
            error.value = err.message
        }
    }

    async function deleteStudent(student) {
        const studentIdeas = getStudentIdeas(student)

        if (studentIdeas.length > 0) {
            error.value = "This student is assigned to one or more ideas. Remove them from those ideas first."
            return false
        }

        try {
            const response = await fetch(`${API_URL}/students/${student.id}/`, {
                method: "DELETE",
            })

            if (!response.ok) {
                throw new Error(`Delete failed: ${response.status}`)
            }

            students.value = students.value.filter(current => current.id !== student.id)

            return true

        } catch (err) {
            console.error(err)
            error.value = "Failed to delete student."
            return false
        }
    }


    // ============================================================
    // MEETING MUTATIONS
    // ============================================================

    async function saveMeeting(payload, existingId = null) {
        try {
            const url = existingId
                ? `${API_URL}/meetings/${existingId}/`
                : `${API_URL}/meetings/`

            const response = await fetch(url, {
                method: existingId ? "PATCH" : "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            })

            if (!response.ok) {
                const data = await response.json().catch(() => null)
                throw new Error(data ? JSON.stringify(data) : `Meeting request failed: ${response.status}`)
            }

            const savedMeeting = await response.json()

            if (existingId) {
                const index = meetings.value.findIndex(meeting => meeting.id === savedMeeting.id)
                if (index !== -1) {
                    meetings.value[index] = savedMeeting
                }
            } else {
                meetings.value.push(savedMeeting)
            }

            return savedMeeting

        } catch (err) {
            console.error(err)
            error.value = err.message
        }
    }

    async function deleteMeeting(meeting) {
        try {
            const response = await fetch(`${API_URL}/meetings/${meeting.id}/`, {
                method: "DELETE",
            })

            if (!response.ok) {
                throw new Error(`Delete failed: ${response.status}`)
            }

            meetings.value = meetings.value.filter(current => current.id !== meeting.id)

            return true

        } catch (err) {
            console.error(err)
            error.value = "Failed to delete meeting."
            return false
        }
    }


    return {
        // state
        ideas, students, meetings, loading, error,
        // computed
        activeIdeas, archivedIdeas,
        // fetch
        fetchData,
        // lookups
        getIdea, getStudent, getIdeaStudents, getIdeaMeetings, getStudentIdeas,
        // idea mutations
        updateStatus, updatePriority, archiveIdea, unarchiveIdea, createIdea, updateIdeaStudents,
        // student mutations
        saveStudent, deleteStudent,
        // meeting mutations
        saveMeeting, deleteMeeting,
    }
})
