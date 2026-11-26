<template>
  <!-- 自定义图片预览 -->
  <div v-if="previewVisible" class="image-preview-overlay" @click="closePreview">
    <div class="image-preview-container" @click.stop>
      <div class="image-preview-toolbar">
        <button class="image-preview-btn" @click="zoomOut" title="缩小">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </button>
        <button class="image-preview-btn" @click="zoomIn" title="放大">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
        </button>
        <button class="image-preview-btn" @click="rotateLeft" title="逆时针旋转">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M1 4v6h6"></path>
            <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
          </svg>
        </button>
        <button class="image-preview-btn" @click="rotateRight" title="顺时针旋转">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6"></path>
            <path d="M20.49 15a9 9 0 1 1-2.13-9.36L23 10"></path>
          </svg>
        </button>
        <button class="image-preview-btn image-preview-btn-reset" @click="resetTransform" title="重置">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6"></path>
            <path d="M1 20v-6h6"></path>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10"></path>
            <path d="M20.49 15a9 9 0 0 1-14.85 3.36L1 14"></path>
          </svg>
        </button>
        <button class="image-preview-close" @click="closePreview" title="关闭">×</button>
      </div>
      <div 
        class="image-preview-img-wrapper"
        @mousedown="startDrag"
        @mousemove="onDrag"
        @mouseup="stopDrag"
        @mouseleave="stopDrag"
        @touchstart="startDrag"
        @touchmove="onDrag"
        @touchend="stopDrag"
      >
        <img 
          :src="previewImage" 
          class="image-preview-img" 
          :style="imgStyle"
          alt="预览图片" 
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const previewVisible = ref(false)
const previewImage = ref('')
const scale = ref(1)
const rotation = ref(0)
const positionX = ref(0)
const positionY = ref(0)
const isDragging = ref(false)
const startX = ref(0)
const startY = ref(0)

const imgStyle = computed(() => {
  return {
    transform: `translate(${positionX.value}px, ${positionY.value}px) scale(${scale.value}) rotate(${rotation.value}deg)`,
    transition: isDragging.value ? 'none' : 'transform 0.2s ease-out'
  }
})

const openPreview = (imageUrl) => {
  previewImage.value = imageUrl
  previewVisible.value = true
  scale.value = 1
  rotation.value = 0
  positionX.value = 0
  positionY.value = 0
  isDragging.value = false
  document.body.style.overflow = 'hidden'
}

const closePreview = () => {
  previewVisible.value = false
  previewImage.value = ''
  scale.value = 1
  rotation.value = 0
  positionX.value = 0
  positionY.value = 0
  isDragging.value = false
  document.body.style.overflow = ''
}

const zoomIn = () => {
  scale.value = Math.min(scale.value + 0.25, 5)
}

const zoomOut = () => {
  scale.value = Math.max(scale.value - 0.25, 0.25)
}

const rotateLeft = () => {
  rotation.value -= 90
}

const rotateRight = () => {
  rotation.value += 90
}

const resetTransform = () => {
  scale.value = 1
  rotation.value = 0
  positionX.value = 0
  positionY.value = 0
}

// 拖动功能
const startDrag = (e) => {
  if (scale.value <= 1) return
  
  isDragging.value = true
  const clientX = e.clientX || e.touches?.[0]?.clientX
  const clientY = e.clientY || e.touches?.[0]?.clientY
  startX.value = clientX - positionX.value
  startY.value = clientY - positionY.value
}

const onDrag = (e) => {
  if (!isDragging.value || scale.value <= 1) return
  
  e.preventDefault()
  const clientX = e.clientX || e.touches?.[0]?.clientX
  const clientY = e.clientY || e.touches?.[0]?.clientY
  positionX.value = clientX - startX.value
  positionY.value = clientY - startY.value
}

const stopDrag = () => {
  isDragging.value = false
}

// ESC键关闭预览
document.addEventListener('keydown', (e) => {
  if (!previewVisible.value) return
  
  if (e.key === 'Escape') {
    closePreview()
  } else if (e.key === '+' || e.key === '=') {
    zoomIn()
  } else if (e.key === '-') {
    zoomOut()
  } else if (e.key === 'ArrowLeft') {
    rotateLeft()
  } else if (e.key === 'ArrowRight') {
    rotateRight()
  } else if (e.key.toLowerCase() === 'r') {
    resetTransform()
  }
})

defineExpose({
  openPreview
})
</script>

<style>
/* 自定义图片预览样式 */
.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999;
  animation: fadeIn 0.2s ease-out;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.image-preview-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.image-preview-toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  background: rgba(0, 0, 0, 0.6);
  padding: 12px 20px;
  border-radius: 50px;
  backdrop-filter: blur(10px);
}

.image-preview-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  cursor: pointer;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.image-preview-btn svg {
  width: 20px;
  height: 20px;
}

.image-preview-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.image-preview-btn:active {
  transform: scale(0.95);
}

.image-preview-btn-reset {
  margin-right: 8px;
}

.image-preview-close {
  width: 44px;
  height: 44px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  font-size: 28px;
  font-weight: bold;
  cursor: pointer;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  line-height: 1;
}

.image-preview-close:hover {
  background: rgba(255, 255, 255, 0.4);
  transform: scale(1.1);
}

.image-preview-img-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 90vw;
  max-height: 75vh;
  overflow: hidden;
  cursor: grab;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.image-preview-img-wrapper:active {
  cursor: grabbing;
}

.image-preview-img {
  max-width: 100%;
  max-height: 75vh;
  border-radius: 8px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
  object-fit: contain;
  pointer-events: none;
}
</style>
