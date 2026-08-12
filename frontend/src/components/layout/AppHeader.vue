<script setup>
defineProps({
    currentView: { type: String, required: true },
    darkMode: { type: Boolean, required: true },
    studentsCount: { type: Number, default: 0 },
    upcomingMeetingsCount: { type: Number, default: 0 },
})

const emit = defineEmits(["change-view", "toggle-dark-mode", "create"])

const views = ["kanban", "students", "meetings"]

const createLabel = {
    kanban: "+ New Idea",
    students: "+ Add Student",
    meetings: "+ Schedule Meeting",
}
</script>

<template>
    <header class="shrink-0 border-b border-slate-200 bg-white/90 px-6 py-4 backdrop-blur-xl dark:border-white/[0.06] dark:bg-[#0d0f14]/90">

        <div class="flex items-center justify-between">

            <div class="flex items-center gap-8">

                <div>
                    <p class="text-xs font-medium text-indigo-500">Innovation Center</p>
                    <h1 class="text-xl font-bold tracking-tight">Student Ideas</h1>
                </div>

                <nav class="hidden items-center gap-1 rounded-xl bg-slate-100 p-1 dark:bg-white/[0.04] md:flex">
                    <button
                        v-for="view in views"
                        :key="view"
                        @click="emit('change-view', view)"
                        :class="currentView === view
                            ? 'bg-white text-slate-900 shadow-sm dark:bg-white/[0.08] dark:text-white'
                            : 'text-slate-500 dark:text-slate-400'"
                        class="rounded-lg px-4 py-2 text-xs font-medium capitalize transition"
                    >
                        {{ view }}
                        <span v-if="view === 'students'" class="ml-1 text-[10px] opacity-50">{{ studentsCount }}</span>
                        <span v-if="view === 'meetings'" class="ml-1 text-[10px] opacity-50">{{ upcomingMeetingsCount }}</span>
                    </button>
                </nav>

            </div>

            <div class="flex items-center gap-2">

                <button
                    @click="emit('toggle-dark-mode')"
                    class="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 text-sm dark:border-white/[0.08]"
                >
                    {{ darkMode ? "☀" : "☾" }}
                </button>

                <button
                    @click="emit('create')"
                    class="rounded-xl bg-indigo-500 px-4 py-2.5 text-xs font-medium text-white shadow-lg shadow-indigo-500/20 hover:bg-indigo-600"
                >
                    {{ createLabel[currentView] }}
                </button>

            </div>

        </div>

        <!-- Mobile navigation -->
        <div class="mt-4 flex gap-1 overflow-x-auto md:hidden">
            <button
                v-for="view in views"
                :key="view"
                @click="emit('change-view', view)"
                :class="currentView === view
                    ? 'bg-indigo-500 text-white'
                    : 'bg-slate-100 text-slate-500 dark:bg-white/[0.04] dark:text-slate-400'"
                class="rounded-lg px-4 py-2 text-xs font-medium capitalize"
            >
                {{ view }}
            </button>
        </div>

    </header>
</template>
