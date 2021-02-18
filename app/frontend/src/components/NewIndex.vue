<template>
  <body>
    <div class="split left" v-if="isConnectionMade">
        <br />
        <h3>Pipes currently in SESAM</h3>
        <br />
        <br />
        <div class="checkboxes_idx">
        <li class="list_idx" v-for="(pipe, index) in scan_pipes" :key="index">
            <input
            :id="pipe"
            :value="pipe"
            name="table"
            type="checkbox"
            class="checkbox"
            v-model="selected_pipes"
            />
            {{ pipe }}
        </li>
        </div> 
        <br />
        <br />
        <br />
          <li class="list_select_all">
            <input
              type="radio"
              class="checkbox_select_all"
              v-on:click="selectAll"
            />
            {{ this.select_all_string }}
          </li>
        <br />       
    </div>
    <div class="split right" v-if="isConnectionMade">
        <br />
        <h3>Autoflow choice</h3>
        <br />
        <button class="choice_button" v-on:click.prevent="mergeIntoGlobals">Merge into globals</button>
        <br />
        <img
          class="sesam_base_img"
          src="https://docs.sesam.io/_images/datahub.jpg"
          alt="sesam_base_img"
        />     
    </div>
    <div v-if="isBufferActive" name="buffer" class="split right">
        <span v-html="bufferIcon()"></span>
    </div>
    <div v-if="is404" class="center_idx">
        <span> {{scan_pipes}} </span>
    </div>
    <div v-if="isGlobalBufferActive" class="center_idx" id="Buffer">
      <span v-html="bufferIcon()"></span>
    </div>
    <div v-if="isSesamResponse" class="center_idx" id="sesamResponse">
      <br />
      <br />
      <h2>{{ result["sesam_result"] }}</h2>
    </div>
    <div>
      <component
        :selected_pipes="selected_pipes"
        class="component"
        v-if="isMergeOfGlobals"
        :is="nextComponent"
      ></component>
    </div>
  </body>
</template>
  
<script>
import api from "../api";
import Globals from "./NewGlobals";
export default {
  name: "NewIndex",
  data: () => {
    return {
      isConnectionMade: false,
      isCheckAll: false,
      isMergeOfGlobals: false,
      isSesamResponse: false,
      isBufferActive: false,
      isGlobalBufferActive: false,
      select_all_string: "Select All",
      is404: false,
      scan_pipes: [],
      selected_pipes: [],
      nextComponent: "Globals",
    };
  },
  components: {
    Globals
  },
  async mounted() {
      let pipes = this.scan_pipes;
      await fetch("http://localhost:5000/get_all_pipes", {
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
    mergeIntoGlobals() {
      this.isMergeOfGlobals = true;
      this.isConnectionMade = false;
    },  
    bufferIcon() {
      return '<img src="https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif" alt="Loading GIF">';
    },
    selectAll() {
      this.isCheckAll = !this.isCheckAll;
      this.selected_pipes = [];
      if(this.isCheckAll){ // Check all
        this.selected_pipes = this.scan_pipes;
      }
    },
    checkOne() {
      this.selected_option = [];
    },
    checkTestOne() {
      this.selected_test_choice = [];
    },
    sesamResponse() {
      api.getResource("/sesam_response").then((data) => {
          //eslint-disable-next-line no-console
          //console.log("testing this...");
          //eslint-disable-next-line no-console
          //console.log(data["result"][0]);
          if (data["result"][0] == "Could not fetch pipes from Sesam."){
            this.scan_pipes = data["result"];
            this.is404 = true;
            data = null;
          }
          if (data["result"][0] == "It seems like your Sesam instance is empty"){
            this.scan_pipes = "It seems like your Sesam instance is empty. Get some pipes in there and hurry back!";
            this.is404 = true;
            data = null;
          }
          if (data != null && data != "") {
            this.scan_pipes = data["result"];
            this.isConnectionMade = true;
          }
      });
    },
  },
};
</script>
  
<style>
input {
  padding: 10%;
  text-align: center;
  width: 40%;
  height: 40px;
  padding: 5px 10px;
  font-size: 12px;
  color: rgba(0, 0, 0);
  letter-spacing: 1px;
  background: #fff;
  border: 2px solid #fff;
}

.choice_button {
  width: 30%;
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

.center_idx {
  padding: 10%;
}

.list_select_all {
  text-align: center;
}

.component {
  width: 100%;
  text-align: center;
}

.checkboxes_idx {
  height: auto;
  max-height: 600px;
  overflow-y: scroll;
}
.checkboxes_idx input {
  vertical-align: middle;
}
.checkboxes_idx label span {
  vertical-align: middle;
}

.left {
  left: 0;
}

.right {
  right: 0;
}

.split {
  height: 100%;
  width: 50%;
  position: fixed;
  z-index: 1;
  top: 20;
  overflow-x: hidden;
  padding-top: 20px;
}

.checkbox_option {
  text-align: center;
  width: 5%;
  background: #fff;
}

.checkbox_select_all {
  width: 5%;
  background: #fff;
  vertical-align: middle;
}

.list_select_all {
  font-size: 12px;
  text-align: center;
  display: block;
}

.list_idx {
  font-size: 12px;
  text-align: left;
  display: block;
}

.sesam_base_img {
  margin-top: 10%;
  height: auto;
  width: 700px;
}

body {
  background-color: rgb(255, 255, 255);
  box-sizing: border-box;
  color: rgb(61, 57, 53);
  display: block;
  font-family: museo-sans-rounded, sans-serif;
  font-size: 14px;
  font-style: normal;
  height: 720px;
  letter-spacing: 0.2px;
  line-height: 10px;
  margin-bottom: 0px;
  margin-left: 0px;
  margin-right: 0px;
  margin-top: 0px;
  text-size-adjust: 100%;
  width: 100%;
}

</style>