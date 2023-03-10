// This example uses MediaRecorder to record from a live audio stream,
// and uses the resulting blob as a source for an audio element.
//
// The relevant functions in use are:
//
// navigator.mediaDevices.getUserMedia -> to get audio stream from microphone
// MediaRecorder (constructor) -> create MediaRecorder instance for a stream
// MediaRecorder.ondataavailable -> event to listen to when the recording is ready
// MediaRecorder.start -> start recording
// MediaRecorder.stop -> stop recording (this will generate a blob of data)
// URL.createObjectURL -> to create a URL from a blob, which we can use as audio src


var recordButton, stopButton, recorder;
var model = "MTK_ch";
// var speak_button = document.getElementById("speak");
var audio_response = ""
var last_response = "";
var defaultVideoSrc = "";


$(document).ready(function () {
  recordButton = document.getElementById('start');
  stopButton = document.getElementById('stop');
  recordButton.disabled = true;
  stopButton.disabled = true;
  record_init();
});

function record_init() {
  navigator.mediaDevices.getUserMedia({
    audio: true, video: false
  })
    .then(function (stream) {
      recordButton.disabled = false;
      recordButton.addEventListener('click', startRecording);
      stopButton.addEventListener('click', stopRecording);
      try {
        // chrome
        recorder = new MediaRecorder(stream, { mimeType: 'video/webm;codecs=vp9' });
      } catch (e) {
        // safari
        recorder = new MediaRecorder(stream);
      }
      recorder.addEventListener('dataavailable', onRecordingReady);
    })
    .catch(function (err) {
      console.log(err);
    });
};


function click_disappear() {
  record_btn = document.getElementById('start');
  stop_btn = document.getElementById('stop');
  record_text = document.getElementById("record_text");
  stop_text = document.getElementById('stop_text');
  if (record_btn.style.display == "none") {
    record_btn.style.display = 'flex';
    record_text.style.display = '';
    stop_btn.style.display = "none";
    stop_text.style.display = "none";
  }
  else {
    record_btn.style.display = 'none';
    stop_btn.style.display = "flex";
    record_text.style.display = 'none';
    stop_text.style.display = "";
  }

}
function startRecording() {
  recordButton.disabled = true;
  stopButton.disabled = false;

  recorder.start();
}

function stopRecording() {
  recordButton.disabled = false;
  stopButton.disabled = true;
  // Stopping the recorder will eventually trigger the `dataavailable` event and we can complete the recording process
  recorder.stop();
}

function onRecordingReady(e) {
  var audio = document.getElementById('audio');
  audio.src = URL.createObjectURL(e.data);
  upload(e.data);
}
// this function is for upoading recognized voice file
function upload(blob) {

  var formData = new FormData();
  formData.append("model", model);
  formData.append("file", blob, "file");
  var audio2 = document.getElementById('audio2');
  try {
    $.ajax({
      method: "POST",
      url: "/recognition",
      data: formData,
      processData: false,
      contentType: false,
    })
      .done(function (result) {
        console.log("Result: " + result.msg);
        console.log(result);
        // audio2.src = URL.createObjectURL(result.data);
        let sum_intext = document.getElementById("intext_sums");
        let new_intext = document.getElementById("intext_news");
        new_intext.innerText = result['news_body'];
        // sum_intext.innerText = result['Summary'];
        for(i = 0; i < result['Summary'].length; i++){
          sum_intext.innerText += (i + 1) + ": " + result['Summary'][i];
        }
        // alert("回傳成功");
      })
      .fail(function (result) {
        console.log("FAILED: " + result);
      });


  } catch (e) {
    console.log("Error catched");
    alert(e.message);
  }

  // document.getElementById("outputSentence").innerHTML="辨識結果:\n"+res.replaceAll(';','\n');
}
// this function will
