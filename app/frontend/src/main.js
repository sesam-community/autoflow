import Vue from 'vue'
import App from './App'
import VueRouter from 'vue-router'
import Index from './components/NewIndex'
import Globals from './components/NewGlobals'
import VueDraggable from "vue-draggable";

Vue.config.productionTip = false
Vue.use(VueDraggable);

const routes = [{
    path: '/sesam_response',
    components: Index
  },
  {
    path: '/get_pipes',
    components: Globals
  }
]

const router = new VueRouter({
  routes,
  mode: 'history'
})

new Vue({
  el: '#app',
  router,
  render: h => h(App)
});