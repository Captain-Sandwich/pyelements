function cardNode(x) {
    var div = document.createElement("div");
    switch(x) {
    case 1:
        div.className = "card open one";
        div.textContent = "1";
        break;
    case 2:
        div.className = "card open two";
        div.textContent = "2";
        break;
    case 3:
        div.className = "card open three";
        div.textContent = "3";
        break;
    case 4:
        div.className = "card open four";
        div.textContent = "4";
        break;
    case 5:
        div.className = "card open five";
        div.textContent = "5";
        break;
    case 6:
        div.className = "card open six";
        div.textContent = "6";
        break;
    case 0:
        div.className = "card hidden";
        div.textContent = "ELEMENTS";
    };
    return div
};

function popCard(x) {
    var hand = document.getElementById("hand_player");
    children = hand.children;
    if (x >= 0 && x < children.length) {
        card = children.item(x);
        hand.removeChild(card);
        return true;
    }
    else {return false;};
};

function getElementIndex(node) {
    var index = 0;
    while ( (node = node.previousElementSibling) ) {
        index++;
    }
    return index;
}

function popThis(obj) {
    index = getElementIndex(obj);
    parent = obj.parentNode;
    parent.removeChild(obj);
    return index;
}

function makePlayerCardCallback (self, val) {
    return function () {
        clickCard(self);
        socket.emit('move', {'game':game_id, 'type':'play', 'target': val});
    }
}

function makeMiddleCardCallback (self, val) {
    return function () {
        clickCard(self);
        socket.emit('move', {'game': game_id, 'type':'take', 'target':val});
    }
}

function clickCard(self) {
    index = popThis(self); // then use index to check logic with server
    console.log(state.playerCards[index])
//    state.playerCards.splice(index, 1)
//    updateAll();
}

function addHidden(x) {
    newCard = cardNode(0);
    var element = document.getElementById("hand_hidden");
    element.appendChild(newCard);
    return true;
};

function addToElement(x, id) {
    newCard = cardNode(x);
    var element = document.getElementById(id);
    element.appendChild(newCard);
    return true;
}

function addMiddle(x) {
    state.middleCards.push(x)
    newCard = cardNode(x);
    newCard.addEventListener("click", makeMiddleCardCallback(newCard, x));
    var middle = document.getElementById("middle");
    middle.appendChild(newCard);
    //updateAll();
    return true;
}

function addOther(x) {
    if (x >= 1 && x <=6){
        newCard = cardNode(x);
        newCard.addEventListener("click", makePlayerCardCallback(newCard, x));
        var element = document.getElementById("hand_hidden");
        element.appendChild(newCard);
        //updateAll();
        return true;
    }
    else {
        return false;
    }
};

function addCard(x) {
    if (x >= 1 && x <=6){
    state.playerCards.push(x)
    newCard = cardNode(x);
    newCard.addEventListener("click", makePlayerCardCallback(newCard, x));
    var element = document.getElementById("hand_player");
    element.appendChild(newCard);
    //updateAll();
    return true;
    }
    else {
        return false;
    }
};

function sum(array){
    return array.reduce( (prev, curr) => prev + curr , 0);
}

function scorePlayer(x) {
    box = document.getElementById("score player");
    box.textContent = x.toString();
}

function scoreMiddle(x) {
    box = document.getElementById("score middle");
    box.textContent = x.toString();
}

function randomCard() {
    x = Math.floor(Math.random() * 6);
    addCard(x);
};

function updateAll(){
    //scorePlayer(sum(state.playerCards));
    //scoreMiddle(sum(state.middleCards));
}

var state = {};
state.playerCards = [];
state.middleCards = [];
state.playerScore = 0;
state.middleScore = 0;

window.onload = function(){
    document.getElementById('knock').addEventListener("click", () => socket.emit('move', {'game':game_id, 'type':'knock'}));
    document.getElementById('drop6').addEventListener("click", () => socket.emit('move', {'game':game_id, 'type':'drop6'}));
}


function updateState(gameState) {
    while (document.querySelector('.card')){
        document.querySelector('.card').remove()
    }
    gameState.playerHand.forEach(function(c) {
        addCard(c);
    });
    gameState.board.forEach(function(c) {
        addMiddle(c);
    });
    gameState.playerBoard.forEach(function(c) {
        addToElement(c,'board');
    });
    gameState.otherBoard.forEach(function(c) {
        addToElement(c,'board_other');
    });
    console.log(gameState);
    if (gameState.gameOver) {
        gameState.otherHandCards.forEach(function (c) {
            addOther(c);
        });
    }
    else {
        for (i = 0; i < gameState.otherHand; i++) {
            addHidden();
        }
    };
    scorePlayer(gameState.playerScore);
    scoreMiddle(gameState.limit);
    if (gameState.playerActive) {
        document.getElementById("other").classList.remove('active')
        document.getElementById("player").classList.add('active')
    }
    else {
        document.getElementById("player").classList.remove('active')
        document.getElementById("other").classList.add('active')
    }
}
console.log(gameState)

socket.on("game", updateState)
