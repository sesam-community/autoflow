<template>
  <body id="app">
    <div v-if="preSelection" class="sesam" id="sesamResponse">
      <h3>
        Give your globals preferred names and move your tables around to assign
        them to your globals
      </h3>
      <div
        class="drag-container"
        v-drag-and-drop:options="options"
        v-on:keyup.enter="createGlobals"
      >
        <ul class="drag-list">
          <li class="drag-column" v-for="group in groups" :key="group.id">
            <br>
            <input disabled v-if="group.name === 'Default List'"
              v-model="group.name"
              class="input_globals"
              :groups="groups"
              :data-id="group.name"
            />
            <input v-if="group.name != 'Default List'"
              v-model="group.name"
              class="input_globals"
              :groups="groups"
              :data-id="group.name"
              value="Global-pipe name"
              @change="onGlobalNameChange"
            />
            <vue-draggable-group
              v-model="group.items"
              :groups="groups"
              :data-id="group.id"
              @change="onGroupsChange"
            >
              <ul class="drag-inner-list" :data-id="group.id">
                <li
                  class="drag-item"
                  v-for="item in group.items"
                  :key="item.id"
                  :data-id="item.id"
                >
                  <div class="drag-item-text">{{ item.name }}</div>
                </li>
              </ul>
            </vue-draggable-group>
          </li>
        </ul>
      </div>
      <button v-on:click.prevent="createGlobals">Merge into Globals</button>
    </div>   
    <div v-if="isBufferActive" class="center" id="Buffer">
      <span v-html="bufferIcon()"></span>
    </div>
    <div v-if="isFinishedModelling" class="modelling" name="last stage">
      <br />
      <br />
      <h3>{{ result["sesam_result"] }}</h3>
      <h3>Follow the below link to look at your new data flows!</h3>
      <br />
      <a href="https://portal.sesam.io/dashboard">Sesam Portal</a>
    </div>
  </body>
</template>
  
  <script>
import api from "../api";
export default {
  name: "Meta",
  data: () => {
    return {
      preSelection: true,
      isBufferActive: false,
      isFinishedModelling: false,
      result: "{{result}}",
      groups: [],
      options: {
        dropzoneSelector: ".drag-inner-list",
        draggableSelector: ".drag-item",
      },
    };
  },
  props: ["selected_pipes"],
  async mounted() {
      let pipes = this.selected_pipes;
      await fetch("http://localhost:5000/create_global_list", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          pipes: pipes,
        }),
      });
      this.sesamResponse();
  },
  methods: {
    bufferIcon() {
      return '<img src="https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif" alt="Loading GIF">';
    },
    sesamResponse() {
      api.getResource("/sesam_response").then((data) => {
        if (data != null && data != "") {
          //eslint-disable-next-line no-console
          //console.log("testing this...");
          //eslint-disable-next-line no-console
          //console.log(data);
          this.groups = data["result"];
        }
      });
    },
    async createGlobals() {
      let globalGroups = this.groups;
      this.preSelection = false;
      this.isBufferActive = true;
      await fetch("http://localhost:5000/create_globals", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          globalGroups: globalGroups,
        }),
      });
      this.globalResponse();
    },
    globalResponse() {
      api.getResource("/sesam_response").then((data) => {
        if (data != null && data != "") {
          //eslint-disable-next-line no-console
          //console.log("testing this...");
          //eslint-disable-next-line no-console
          //console.log(data);
          this.result = data;
          this.isFinishedModelling = true;
          this.isBufferActive = false;
        }
      });
    },
    onGroupsChange(e) {
      //eslint-disable-next-line no-console
      console.log({ e });
      //eslint-disable-next-line no-console
      console.log(this.groups[2].name);
      if (this.groups[2].items.length == 1) {
        //eslint-disable-next-line no-console
        console.log(this.groups[2].items[0].name);
      }
    
    },
    onGlobalNameChange(e) {
      //eslint-disable-next-line no-console
      console.log({ e });
    },
  },
};
</script>

<style lang="scss">
$ease-out: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
$first-global: #f4ce46;
$second-global: #2a92bf;
$third-global: #00b961;
$fourth-global: #b9004d;

* {
  box-sizing: border-box;
}

a {
  font-size: 14px;
}

p {
  font-size: 14px;
}

.center {
  padding: 10%;
}

.modelling {
  padding: 10%;
}

.input_globals {
  padding: 5%;
  text-align: center;
  width: 90%;
  height: 40px;
  padding: 5px 10px;
  font-size: 12px;
  letter-spacing: 1px;
  background: #fff;
  border: 2px solid #fff;
}

button {
  width: 20%;
  margin: 5px;
  padding: 5px 10px;
  font-size: 12px;
  letter-spacing: 1px;
  background: #009fdf;
  height: 40px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #fff;
  -webkit-transition: all 0.1s ease-in-out;
  -moz-transition: all 0.1s ease-in-out;
  -ms-transition: all 0.1s ease-in-out;
  -o-transition: all 0.1s ease-in-out;
  transition: all 0.1s ease-in-out;
}

.drag-container {
  display: table;   /* Allow the centering to work */
	margin: 0 auto;
}

.drag-list {
  display: flex;
  width: 1000px;
  height: 600px;
  align-items: flex-start;

  @media (max-width: 690px) {
    display: block;
  }
}

.drag-column {
  flex: 1;
  margin: 0 10px;
  height: 600px;
  position: relative;
  overflow: hidden;

  @media (max-width: 690px) {
    margin-bottom: 30px;
  }

  h2 {
    font-size: 0.8rem;
    margin: 0;
    font-weight: 600;
  }

  &-first-global {
    .drag-column-header,
    .drag-options {
      background: $first-global;
    }
  }

  &-second-global {
    .drag-column-header,
    .drag-options {
      background: $second-global;
    }
  }

  &-third-global {
    .drag-column-header,
    .drag-options {
      background: $third-global;
    }
  }

  &-fourth-global {
    .drag-column-header,
    .drag-options {
      background: $fourth-global;
    }
  }
}

.drag-column-header {
  justify-content: space-between;
  padding: 10px;
  user-select: none;
}

.drag-inner-list {
  height: 85vh;
  overflow: auto;
}

.drag-item {
  margin: 10px;
  height: 50px;
  background: rgba(#009fdf, 0.7);
  transition: $ease-out;

  /* items grabbed state */
  &[aria-grabbed="true"] {
    background: #009fdf;
    color: #fff;
  }

  .drag-item-text {
    font-size: 1rem;
    padding-left: 0rem;
    padding-top: 1rem;
  }
}

.drag-header-more {
  cursor: pointer;
}

@keyframes nodeInserted {
  from {
    opacity: 0.2;
  }
  to {
    opacity: 0.8;
  }
}

.item-dropzone-area {
  height: 3rem;
  background: rgba(44, 39, 39, 0.733);
  opacity: 0.8;
  animation-duration: 0.5s;
  animation-name: nodeInserted;
  margin-left: 0.6rem;
  margin-right: 0.6rem;
}
</style>