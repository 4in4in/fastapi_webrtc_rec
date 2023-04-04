const video = document.getElementById("video");
const button = document.getElementById("action-button");
const log = console.log;

var peerConnection = null;
var userMedia = null;

const changeButtonToStart = () => (button.innerText = "Start");
const changeButtonToStop = () => (button.innerText = "Stop");

changeButtonToStart();

const config = {
    sdpSemantics: "unified-plan",
    iceServers: [{ urls: ["stun:stun.l.google.com:19302"] }],
};

function createPeerConnection() {
    peerConnection = new RTCPeerConnection(config);

    peerConnection.addEventListener("icegatheringstatechange", () => log(peerConnection.iceGatheringState), false);
    peerConnection.addEventListener("iceconnectionstatechange", () => log(peerConnection.iceConnectionState), false);
    peerConnection.addEventListener("signalingstatechange", () => log(peerConnection.signalingState), false);
    peerConnection.addEventListener("track", event => event.track.kind === "video" && (video.srcObject = event.streams[0]));

    return peerConnection;
}

async function negotiate() {
    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);
    await new Promise(resolve => {
        if (peerConnection.iceGatheringState === "complete") {
            resolve();
        } else {
            function checkState() {
                if (peerConnection.iceGatheringState === "complete") {
                    peerConnection.removeEventListener("icegatheringstatechange", checkState);
                    resolve();
                }
            }
            peerConnection.addEventListener("icegatheringstatechange", checkState);
        }
    });
    /// it is possible to set audio and video codecs
    const response = await fetch("/offer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            sdp: peerConnection.localDescription.sdp,
            type: peerConnection.localDescription.type,
        }),
    });
    const remoteDescription = await response.json();
    peerConnection.setRemoteDescription(remoteDescription);
}

async function start() {
    button.disabled = true;

    peerConnection = createPeerConnection();
    const constraints = {
        audio: true,
        video: {
            width: 640,
            height: 480,
        },
        // video: true,
        /// or can specify width, height
    };
    userMedia = await navigator.mediaDevices.getUserMedia(constraints);
    userMedia.getTracks().forEach(t => peerConnection.addTrack(t, userMedia));
    await negotiate();

    changeButtonToStop();
    button.disabled = false;
}

async function stop() {
    button.disabled = true;

    if (peerConnection.getTransceivers) {
        peerConnection.getTransceivers().forEach(t => t.stop && t.stop());
    }
    peerConnection.getSenders().forEach(s => s.track.stop());
    peerConnection.close();
    changeButtonToStart();
    button.disabled = false;

    userMedia.getTracks().forEach(t => t.stop());
    peerConnection = null;
}

button.addEventListener("click", event => {
    (!peerConnection ? start : stop)();
});
