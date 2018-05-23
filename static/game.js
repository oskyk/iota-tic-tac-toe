/*
Original(Offline) by: Luiz Bills
Git: https://github.com/luizbills/html5-tic-tac-toe
 */


var ctx = $('#canvas')[0].getContext('2d');
var addr_index = 10;
var player = 0;
var started = false;
var playerTurn = 0; // player 1 ('X') plays first

function append_tx(tx) {
    $('#tx-hashes').append("<p style='display: none' class='tx-hash'><a href='http://open-iota.prizziota.com/#/search/tx/" + tx + "' target='_blank'>" + tx + "</a></p>");
    $('#tx-hashes').find('.tx-hash:last').slideDown('slow');
}

function save_move(player, x, y) {
    $.post('move', {'addr_index': addr_index, 'player': player, 'x': x, 'y': y}, function (data) {
        append_tx(data['tx_hash']);
        wait_for_move(gameGrid._moveCount, gameGrid);
    });
}

function wait_for_move(id, grid) {
    $('#game-msg').text('Waiting for other player');
    $.getJSON('move', {'addr_index': addr_index, 'id': id}, function (data) {
        if (data['player'] === 'x') {
            grid.markCellWithX(parseInt(data['x']), parseInt(data['y']));
        } else {
            grid.markCellWithO(parseInt(data['x']), parseInt(data['y']));
        }
        playerTurn = (playerTurn === 0 ? 1 : 0);
        $('#game-msg').text('Yours turn');
        append_tx(data['tx_hash']);
    }).fail(function () {
        setTimeout(function () {
            wait_for_move(id, grid);
        },500);
    });
}


function Grid() {
    this._positions = [];
    this._moveCount = 0;
    this.draw();
}

(function(Grid) {
    Math.TWO_PI = Math.PI * 2;
    ctx.lineWidth = 5;

    Grid.p = Grid.prototype;
    
    Grid.p.draw = function() {
        var i = 0, x, y, pos;
        ctx.beginPath();
        for (; i < 2; i++) {
            x = 100 + 100*i;
            ctx.moveTo(x, 0);
            ctx.lineTo(x, 300);
        }
        for (i = 0; i < 2; i++) {
    
            y = 100 + 100*i;
            ctx.moveTo(0, y);
            ctx.lineTo(300, y);
        }
        
        ctx.strokeStyle = '#000000';
        ctx.stroke();
        ctx.closePath();
        
        pos = this._positions;
        for (i = 0; i < 9; i ++) {
            x = i % 3 | 0;
            y = i / 3 | 0;
            if (pos[i] === 'x') {
                drawX(x, y);
            } else if (pos[i] === 'o') {
                drawO(x, y);
            }
        }
    };
    
    Grid.p.markCellWithX = function(x, y) {
        this._positions[(y * 3) + x] = 'x';
        this._moveCount++;

        if (this._checkVictory(x, y, 'x')) {
          this.currentState = 'x victory'
        } else if (this._checkDraw()) {
          this.currentState = 'draw';
        }
        this.draw();
    };
    
    Grid.p.markCellWithO = function(x, y) {
        this._positions[(y * 3) + x] = 'o';
        this._moveCount++;

        if (this._checkVictory(x, y, 'o')) {
          this.currentState = 'o victory'
        } else if (this._checkDraw()) {
          this.currentState = 'draw';
        }

        this.draw();
    };
    
    Grid.p.isMarkedCell = function(x, y) {
        return typeof this._positions[(y * 3) + x] !== 'undefined';
    };

    Grid.p.isMarkedCellWith = function(x, y, symbol) {
        return this._positions[(y * 3) + x] === symbol;
    };
    
    /**
    by Hardwareguy 
    http://stackoverflow.com/a/1056352
    */
    Grid.p._checkVictory = function(x, y, symbol) {
      var i;

      //check victory conditions
      //check col
      for(i = 0; i < 3; i++) {
        if(!this.isMarkedCellWith(x, i, symbol)) break;
        if(i == 2) return true;
      }

      //check row
      for(i = 0; i < 3; i++) {
        if(!this.isMarkedCellWith(i, y, symbol)) break;
        if(i == 2) return true;
      }

      //check diag
      if(x == y){
        //we're on a diagonal
        for(i = 0; i < 3; i++) {
          if(!this.isMarkedCellWith(i, i, symbol)) break;
          if(i == 2) return true;
        }
      }

      //check anti diag (thanks rampion)
      for(i = 0; i < 3; i++){
        if(!this.isMarkedCellWith(i, (2 - i), symbol)) break;
        if(i == 2) return true;
      }

      return false;
    };

    Grid.p._checkDraw = function() {
      return this._moveCount == 9;
    };
    
    function drawX(cellX, cellY) {
        var i = 0, dx, dy;
        ctx.beginPath();
        for (i = 0; i < 2; i++) {
            dx = (cellX * 100) + 10 + (80*i);
            dy = (cellY * 100) + 10;
            ctx.moveTo(dx, dy);
            dx = (cellX * 100) + 90 - (80*i);
            dy = (cellY * 100) + 90;
            ctx.lineTo(dx, dy);
        }
        ctx.strokeStyle = '#3333ff';
        ctx.stroke();
        ctx.closePath();
    }
    
    function drawO (cellX, cellY) {
        ctx.beginPath();
        ctx.arc(cellX*100 + 50, 
                cellY*100 + 50, 
                40, 0, Math.TWO_PI, false);
        ctx.strokeStyle = '#ff3333';
        ctx.stroke();
        ctx.closePath();
    }
})(Grid);

gameGrid = new Grid();

$('#canvas').click(function(e) {
  var x, y;
  x = e.offsetX / 100 | 0;
  y = e.offsetY / 100 | 0;
  //console.log(x, y);
    
  if (!gameGrid.isMarkedCell(x, y) && playerTurn === player && started) {
    if (playerTurn === 0) {
      if (gameGrid.markCellWithX(x, y));
      playerTurn = 1;
      save_move('x', x, y);
    } else {
      gameGrid.markCellWithO(x, y);
      playerTurn = 0;
      save_move('o', x, y);
    }

    if (typeof gameGrid.currentState !== 'undefined') {
      var msg = $('#game-msg');
      $('#canvas').off('click');

      if (gameGrid.currentState === 'o victory') {
        msg
          .css('color', '#ff3333')
          .text('RED WINS');
      } else if (gameGrid.currentState === 'x victory') {
        msg
          .css('color', '#3333ff')
          .text('BLUE WINS');
      } else if (gameGrid.currentState === 'draw'){
        msg
          .css('color', '#333333')
          .text('DRAW!');
      }
    }
  }
});


function start_game(Iplayer, index) {
    player = Iplayer;
    addr_index = index;
    started = true;
    if(player !== playerTurn){
        wait_for_move(gameGrid._moveCount, gameGrid);
    }else {
        $('#game-msg').text('Yours turn');
    }
}