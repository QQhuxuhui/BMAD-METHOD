/**
 * Ripple 波纹效果指令
 * 用法: v-ripple 或 v-ripple="{ color: '#fff', duration: 600 }"
 */
import type { Directive } from 'vue'

interface RippleOptions {
  color?: string
  duration?: number
  opacity?: number
}

const defaultOptions: Required<RippleOptions> = {
  color: 'rgba(255, 255, 255, 0.5)',
  duration: 600,
  opacity: 0.5,
}

/**
 * 创建ripple波纹元素
 */
function createRipple(
  event: MouseEvent,
  element: HTMLElement,
  options: Required<RippleOptions>
) {
  const { color, duration, opacity } = options

  // 获取元素位置和尺寸
  const rect = element.getBoundingClientRect()
  const size = Math.max(rect.width, rect.height)
  const x = event.clientX - rect.left - size / 2
  const y = event.clientY - rect.top - size / 2

  // 创建ripple元素
  const ripple = document.createElement('span')
  ripple.className = 'ripple-effect'
  ripple.style.cssText = `
    position: absolute;
    border-radius: 50%;
    pointer-events: none;
    width: ${size}px;
    height: ${size}px;
    left: ${x}px;
    top: ${y}px;
    background-color: ${color};
    opacity: ${opacity};
    transform: scale(0);
    animation: ripple-animation ${duration}ms ease-out;
  `

  // 确保父元素有position定位
  if (getComputedStyle(element).position === 'static') {
    element.style.position = 'relative'
  }

  // 添加overflow hidden以裁剪ripple
  element.style.overflow = 'hidden'

  // 添加到元素中
  element.appendChild(ripple)

  // 动画结束后移除ripple元素
  setTimeout(() => {
    ripple.remove()
  }, duration)
}

/**
 * 注入CSS动画
 */
function injectStyles() {
  if (document.querySelector('#ripple-styles')) {
    return // 已经注入过了
  }

  const style = document.createElement('style')
  style.id = 'ripple-styles'
  style.textContent = `
    @keyframes ripple-animation {
      from {
        transform: scale(0);
        opacity: 0.5;
      }
      to {
        transform: scale(4);
        opacity: 0;
      }
    }
  `
  document.head.appendChild(style)
}

/**
 * Ripple指令
 */
export const vRipple: Directive<HTMLElement, RippleOptions> = {
  mounted(el, binding) {
    // 注入CSS动画
    injectStyles()

    // 合并配置选项
    const options: Required<RippleOptions> = {
      ...defaultOptions,
      ...(binding.value || {}),
    }

    // 添加点击事件监听器
    const handleClick = (event: MouseEvent) => {
      createRipple(event, el, options)
    }

    // 保存到元素上，便于unmounted时移除
    ;(el as any).__rippleHandler = handleClick

    el.addEventListener('click', handleClick)
  },

  unmounted(el) {
    // 移除事件监听器
    const handler = (el as any).__rippleHandler
    if (handler) {
      el.removeEventListener('click', handler)
      delete (el as any).__rippleHandler
    }
  },
}

export default vRipple
