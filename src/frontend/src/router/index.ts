import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'home', component: () => import('../views/HomePage.vue') },
  { path: '/resources/lesson', name: 'lesson', component: () => import('../views/LessonPage.vue') },
  { path: '/resources/quiz', name: 'quiz', component: () => import('../views/QuizPage.vue') },
  { path: '/resources/coding', name: 'coding', component: () => import('../views/CodingPage.vue') },
  { path: '/resources/mindmap', name: 'mindmap', component: () => import('../views/MindmapPage.vue') },
  { path: '/resources/path', name: 'path', component: () => import('../views/StudyPathPage.vue') },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
