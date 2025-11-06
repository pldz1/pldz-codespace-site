import { createStore } from "vuex";

// 博客信息
const authState = {
  namespaced: true,
  state: () => ({
    // 用户信息
    nickname: "",
    username: "",
    avatar: "",
    isadmin: false,
  }),
  actions: {
    // 通过 dispatch 调用这个 action，来提交 mutation
    update({ commit }, data) {
      commit("update", data);
    },
    avatar({ commit }, data) {
      commit("avatar", data);
    },
    reset({ commit }) {
      commit("reset");
    },
  },
  mutations: {
    // mutation 来更新 authState
    update(state, data) {
      if (data) {
        state.username = data?.username || "";
        state.isadmin = data?.isadmin || false;
        state.nickname = data?.nickname || "";
        state.avatar = data?.avatar || "";
      }
    },
    avatar(state, data) {
      if (data) {
        state.avatar = data;
      }
    },
    reset(state) {
      state.nickname = "";
      state.username = "";
      state.avatar = "";
      state.isadmin = false;
    },
  },
};

const uiState = {
  namespaced: true,
  state: () => ({
    loadingMap: {},
  }),
  mutations: {
    setLoading(state, { key, value }) {
      if (!key) return;
      if (value) {
        state.loadingMap = { ...state.loadingMap, [key]: true };
      } else {
        const { [key]: _removed, ...rest } = state.loadingMap;
        state.loadingMap = rest;
      }
    },
  },
  actions: {
    startLoading({ commit }, key) {
      commit("setLoading", { key, value: true });
    },
    stopLoading({ commit }, key) {
      commit("setLoading", { key, value: false });
    },
    setLoading({ commit }, payload) {
      commit("setLoading", payload);
    },
  },
  getters: {
    isLoading: (state) => (key) => !!state.loadingMap[key],
    loadingEntries: (state) => state.loadingMap,
    anyLoading: (state) => Object.values(state.loadingMap).some(Boolean),
  },
};

export default createStore({
  modules: { authState, uiState },
});
