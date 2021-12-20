/*!
 * main.js - v1.0.0 (2021-12-03T20:23)
 * Copyright 2021-2021
 * author Wuzhong Yi 2021/12/03
 */
const dataForm = document.querySelector("#dataForm");
dataForm.onsubmit = submitData;

/**
 * Call the SRT execution
 * @description call the SRT with fetch api
 * @return {response} response.text()
 * @api "/api/srt"
 */
function runSRT() {
  const srtApi = "/api/run/srt";
  updateResult("running...");
  fetch(srtApi, { method: "GET" })
    .then((response) => response.text())
    .then((text) => {
      updateResult(text);
      showFigure();
    })
    .catch((error) => updateResult("Request failed with: " + error));
}

/**
 * Show the processing status
 * @description show the processing status
 * @param {string} message result
 * @return void
 */
function updateResult(res) {
  const log = document.querySelector("#result");
  log.textContent = res;
}

/**
 * Show the figure
 * @description show the figure with fetch api
 * @return {response} response.blob()
 * @api "/api/show/figure"
 */
function showFigure() {
  const image = document.querySelector("img");
  let apiFig = "/api/show/figure";

  fetch(apiFig, { method: "GET" })
    .then((response) => response.blob())
    .then(function (response) {
      let objectURL = URL.createObjectURL(response);
      image.src = objectURL;
      updateResult("mission completed!");
    })
    .catch((error) => updateResult("Request failed with: " + error));
}

/**
 * Submit the form data and run the SRT and show the result figure finally
 * @description rewrite the form submit function and prevent the default submit event
 * @param {event} event form onsubmit event
 * @return {response} response.text()
 * @api "/api/save/file"
 */
function submitData(event) {
  updateResult("saving...");
  let apiSendData = "/api/save/file";

  fetch(apiSendData, {
    method: "POST",
    body: new FormData(dataForm),
  })
    .then((response) => response.text())
    .then((text) => {
      updateResult(text);
      runSRT();
    })
    .catch((error) => updateResult("Request failed with: " + error));
  event.preventDefault();
}
