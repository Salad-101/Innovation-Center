export function getInitials(name) {
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

export function formatDate(date) {
    if (!date) {
        return ""
    }

    return new Intl.DateTimeFormat("en", {
        month: "short",
        day: "numeric",
        year: "numeric",
    }).format(new Date(`${date}T00:00:00`))
}

export function formatTime(time) {
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

export function formatDateTime(datetime) {
    if (!datetime) {
        return ""
    }

    return new Intl.DateTimeFormat("en", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
    }).format(new Date(datetime))
}

// Deterministic color per idea so the same idea always renders the same
// chip color across the calendar, regardless of sort order.
const IDEA_COLOR_PALETTE = [
    "bg-indigo-500",
    "bg-emerald-500",
    "bg-amber-500",
    "bg-rose-500",
    "bg-sky-500",
    "bg-purple-500",
    "bg-teal-500",
    "bg-orange-500",
]

export function getIdeaColor(ideaId) {
    if (ideaId === null || ideaId === undefined) {
        return IDEA_COLOR_PALETTE[0]
    }

    return IDEA_COLOR_PALETTE[Number(ideaId) % IDEA_COLOR_PALETTE.length]
}

// Local calendar date as YYYY-MM-DD. `<input type="date">` values are
// local-calendar dates, so "today" comparisons must use local time too —
// `new Date().toISOString()` returns UTC and drifts a day around midnight
// for timezones ahead of UTC.
export function getLocalToday() {
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, "0")
    const day = String(now.getDate()).padStart(2, "0")

    return `${year}-${month}-${day}`
}

export function isMeetingToday(meeting) {
    return meeting.date === getLocalToday()
}

export function getStatusDotClass(status) {
    return {
        NEW: "bg-blue-500",
        REVIEW: "bg-amber-500",
        REFINEMENT: "bg-orange-500",
        APPROVED: "bg-emerald-500",
        REJECTED: "bg-red-500",
    }[status]
}

export function getPriorityClass(priority) {
    return {
        LOW:
            "border-slate-500/20 bg-slate-500/10 text-slate-500 dark:text-slate-400",

        MEDIUM:
            "border-amber-500/20 bg-amber-500/10 text-amber-600 dark:text-amber-400",

        HIGH:
            "border-red-500/20 bg-red-500/10 text-red-600 dark:text-red-400",
    }[priority]
}
