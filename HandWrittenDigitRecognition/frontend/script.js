const canvas =
document.getElementById("canvas");

const ctx =
canvas.getContext("2d");

ctx.fillStyle = "black";
ctx.fillRect(
    0,
    0,
    canvas.width,
    canvas.height
);

let drawing = false;

canvas.addEventListener(
    "mousedown",
    () => drawing = true
);

canvas.addEventListener(
    "mouseup",
    () => {
        drawing = false;
        ctx.beginPath();
    }
);

canvas.addEventListener(
    "mousemove",
    draw
);

function draw(event)
{
    if(!drawing) return;

    ctx.lineWidth = 20;

    ctx.lineCap = "round";

    ctx.strokeStyle = "white";

    ctx.lineTo(
        event.offsetX,
        event.offsetY
    );

    ctx.stroke();

    ctx.beginPath();

    ctx.moveTo(
        event.offsetX,
        event.offsetY
    );
}

function clearCanvas()
{
    ctx.fillStyle = "black";

    ctx.fillRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    document.getElementById(
        "result"
    ).innerHTML = "";
}

function predictDigit()
{
    canvas.toBlob(blob => {

        let formData =
        new FormData();

        formData.append(
            "file",
            blob,
            "digit.png"
        );

        fetch(
            "http://127.0.0.1:8000/predict",
            {
                method:"POST",
                body:formData
            }
        )
        .then(res => res.json())
        .then(data => {

            document.getElementById("digit").innerText = data.digit;

            document.getElementById("confidence").innerText =
            "Confidence: " +
            (data.confidence * 100).toFixed(2) + "%";
        });

    });
}