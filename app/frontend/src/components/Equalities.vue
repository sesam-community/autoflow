<template>
  <body id="app">
    <div class="equality" v-if="preSelection">
      <button class="open" @click="openCloseAll()">
        <template v-if="allClosed">Open</template>
        <template v-else>Close</template>
        All
      </button>
      <div v-for="(element, index) in this.final_configs" :key="index" class="accordian">
        <h4 @click="element.open = !element.open">{{ element.name }}</h4>
        <span v-if="element.open" v-html="makeString(element.config)"></span>
        <input v-if="element.open" v-model="stringEquality" placeholder='i.e., ["eq", "pip1.email", "pip2.emailAddress"]' type="text" class="equality_input">
        <button v-if="element.open" class="open" v-on:click.prevent="addEquality(element.config)">Add Equality</button>
        <button v-if="element.open" class="open" v-on:click.prevent="resetEquality(element.config)">Remove Equality</button>
      </div>
    </div>
    <div v-if="preSelection">
      <br>
      <br>
      <br>
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
      allClosed: true,
      stringEquality: null,
      final_configs: []
    };
  },
  props: ["groups", "configs_with_equalities"],
  async mounted() {
      let globals = this.groups;
      let globals_with_equalities = this.configs_with_equalities;
      for (let index = 0; index < globals.length; index++) {
        const element = globals[index];
        let schema = {
          "open": null,
          "name": null,
          "config": {
            "_id": null,
            "type": "pipe",
            "source": {
              "type": "merge",
              "datasets": [],
              "equality": [],
              "identity": "first",
              "strategy": "default",
              "version": 2
            },
            "metadata": {
              "global": true,
              "tags": []
            }
          },
        };
        if (element['name'].includes('global-')) {
          schema['name'] = element['name']
          schema['open'] = false
          schema['config']['_id'] = element['name']
          schema['config']['metadata']['tags'] = element['name'].split('-')[1]
          for (let idx = 0; idx < globals_with_equalities.length; idx++) {
            const element_config = globals_with_equalities[idx];
            if (element_config['_id'] == element['name']){
              schema['config']['source']['equality'] = element_config['source']['equality']
            }
          }
          for (let idx = 0; idx < element['items'].length; idx++) {
            const sub_element = element['items'][idx];
            var pip_idx = idx+1;
            schema['config']['source']['datasets'].push(sub_element['name'].concat(" pip"+pip_idx))
          }
          this.final_configs.push(schema);
        }
      }
      //console.log(this.final_configs)
  },
  methods: {
    bufferIcon() {
      return '<img src="https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif" alt="Loading GIF">';
    },
    makeString(config) {
      const stringElement = JSON.stringify(config, null, "\t")
      return `<textarea rows="20" cols="80" style="width: 60%;">${stringElement}</textarea><br />`
    },
    openCloseAll() {
      this.allClosed = !this.allClosed
      if (this.allClosed) this.final_configs.map(x => x.open = false)
      else this.final_configs.map(x => x.open = true)
    },
    resetEquality(element) {
      element['source']['equality'].pop();
    },
    addEquality(element) {
      //console.log(this.stringEquality)
      element['source']['equality'].push(JSON.parse(this.stringEquality.replace(/'/g, '"')));
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
      let globalGroups = this.final_configs;
      let isEquality = true;
      this.preSelection = false;
      this.isBufferActive = true;
      await fetch("http://localhost:5000/globals", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          globalGroups: globalGroups,
          isEquality: isEquality,
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
  },
};
</script>

<style lang="scss">
$ease-out: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
$first-global: #f4ce46;
$second-global: #2a92bf;
$third-global: #00b961;
$fourth-global: #b9004d;

.accordian {
  margin: 8px 0;
  cursor: pointer;
  padding: 0.25em;
}

.center {
  padding: 10%;
}

.equality_input {
  width: 25%;
}
.open {
  width: 15%;
  margin: 5px;
  padding: 5px 10px;
  font-size: 12px;
  letter-spacing: 1px;
  background: #505455;
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

button {
  width: 15%;
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

</style>