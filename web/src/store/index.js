import { createStore } from "vuex";

// 博客信息
const authState = {
  namespaced: true,
  state: {
    username: "",
    isAdmin: false,
  },
  actions: {
    // 通过 dispatch 调用这个 action，来提交 mutation
    update({ commit }, data) {
      commit("setAuthData", data);
    },
  },
  mutations: {
    // mutation 来更新 authState
    setAuthData(state, data) {
      if (data) {
        state.username = data?.username || "";
        state.isAdmin = data?.isAdmin || false;
      }
    },
  },
};

export default createStore({
  modules: { authState },
});
