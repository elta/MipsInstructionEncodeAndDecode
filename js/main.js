
function Debug(str)
{
    var isDebug = 1;

    if (isDebug) {
        console.log(str);
    }
}


function judgeInput()
{
    var output = document.getElementById("last_output");
    var input = document.getElementById("inputText");

    var regex= /, *| *,| *, *|,| /;
    var outputs = input.value.trim().split(regex);
    var result = "";

    Debug(outputs);

    var startC0 = outputs[0][0];
    var startC1 = outputs[0][1];

    if (startC0 >= 'A' && startC0 <= 'z') { // Got inst
        Debug("Got instruction");
        result = encode(outputs);
    } else if (startC0 == '0' && startC1.toLowerCase() == 'x') { // Got HEX value
        result = decode(outputs[0]);
        Debug("Got HEX value");
    } else {
        Debug("Error input");
    }

    input.value = "";
    output.innerHtml = result;
}

