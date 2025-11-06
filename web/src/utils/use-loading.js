import { computed } from "vue";
import { useStore } from "vuex";

/**
 * 统一的 loading 状态管理 hooks
 * @param {string} key 唯一的 loading key
 * @returns {{ isLoading: import("vue").ComputedRef<boolean>, start: Function, stop: Function, set: Function }}
 */
export function useLoading(key) {
  const store = useStore();

  const isLoading = computed(() => store.getters["uiState/isLoading"](key));

  const set = (value) => {
    store.dispatch("uiState/setLoading", { key, value });
  };

  const start = () => set(true);
  const stop = () => set(false);

  return {
    isLoading,
    start,
    stop,
    set,
  };
}
