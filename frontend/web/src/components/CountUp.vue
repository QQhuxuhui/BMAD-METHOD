<template>
  <span ref="countupRef">{{ displayValue }}</span>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { CountUp as CountUpJS } from 'countup.js'

// Props
interface Props {
  /** 结束值 */
  endVal: number
  /** 起始值 */
  startVal?: number
  /** 动画持续时间（秒） */
  duration?: number
  /** 小数位数 */
  decimals?: number
  /** 是否使用千位分隔符 */
  separator?: boolean
  /** 前缀 */
  prefix?: string
  /** 后缀 */
  suffix?: string
}

const props = withDefaults(defineProps<Props>(), {
  startVal: 0,
  duration: 1.5,
  decimals: 0,
  separator: false,
  prefix: '',
  suffix: '',
})

// Refs
const countupRef = ref<HTMLElement>()
const displayValue = ref<string | number>(props.startVal)
let countUp: CountUpJS | null = null

/**
 * 初始化CountUp实例
 */
const initCountUp = () => {
  if (!countupRef.value) return

  const options = {
    startVal: props.startVal,
    duration: props.duration,
    decimalPlaces: props.decimals,
    useEasing: true,
    useGrouping: props.separator,
    separator: props.separator ? ',' : '',
    decimal: '.',
    prefix: props.prefix,
    suffix: props.suffix,
  }

  countUp = new CountUpJS(countupRef.value, props.endVal, options)

  if (!countUp.error) {
    countUp.start()
  } else {
    console.error('CountUp error:', countUp.error)
    displayValue.value = props.endVal
  }
}

/**
 * 更新CountUp值
 */
const updateCountUp = (newVal: number) => {
  if (countUp && !countUp.error) {
    countUp.update(newVal)
  } else {
    // 如果CountUp未初始化或有错误，直接更新显示值
    displayValue.value = newVal
  }
}

// Watch endVal变化
watch(
  () => props.endVal,
  (newVal) => {
    if (countUp) {
      updateCountUp(newVal)
    } else {
      displayValue.value = newVal
    }
  }
)

// Lifecycle
onMounted(() => {
  initCountUp()
})

onBeforeUnmount(() => {
  countUp = null
})
</script>

<style scoped>
span {
  display: inline-block;
}
</style>
