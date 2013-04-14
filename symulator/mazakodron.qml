import Qt 4.7

Rectangle {

    property bool mazak_down: false;
    property bool robot_hidden: false;
    property double constROBOT_R: 119.5;
    property double constWHEEL_R: 18.0;
    property double constREV_STEP: 1.0/512.0;
    property double constSTEP: 0.220875;

    function draw() {
      if (mazak_down) {
        Qt.createQmlObject('import Qt 4.7; Rectangle {'+
          'color: "black";'+
          'width: drawing.width*0.01;'+
          'height: drawing.height*(view.constSTEP/210);'+
          'x: drawing.width*'+mazak.xPos+';'+
          'y: drawing.height*'+mazak.yPos+';'+
          'rotation: '+mazak.rotation+';'+
        '}', drawing, "line");
      }
    }
    function goForward() {
      draw();
      var angle = (mazak.rotation/360)*2*3.14;
      mazak.xPos += (-constSTEP * Math.sin(angle))/297;
      mazak.yPos += (constSTEP * Math.cos(angle))/210;
    }

    function goBackward() {
      draw();
      var angle = (mazak.rotation/360)*2*3.14;
      mazak.xPos -= (-constSTEP * Math.sin(angle))/297;
      mazak.yPos -= (constSTEP * Math.cos(angle))/210;
    }

    function rotateLeft() {
      mazak.rotation -= ((constWHEEL_R*constREV_STEP*360)/constROBOT_R)/8;
    }

    function rotateRight() {
      mazak.rotation += ((constWHEEL_R*constREV_STEP*360)/constROBOT_R)/8;
    }

    function liftMazak() {
      mazak_down = false;
    }

    function dropMazak() {
      mazak_down = true;
    }

    function hideRobot() {
      robot_hidden = true;
    }

    function showRobot() {
      robot_hidden = false;
    }

    id: view
    anchors.fill: parent;
    color: "grey";

    Rectangle {
      id: paper;
      x: view.width/2 - paper.width/2;
      y: view.height/2 - paper.height/2;
      width: Math.min(view.width, view.height*1.41)*0.75;
      height: Math.min(view.height, view.width*0.7)*0.75;
      color: "white";

      Rectangle {
        id: drawing;
        anchors.fill: parent;
        color: "transparent";
      }
      Image {

        property double xPos: 0;
        property double yPos: 0;

        id: mazak;

        x: xPos*paper.width;//.3*paper.width;
        y: yPos*paper.height;//.3*paper.height;
        width: 0;
        height: 0;
        rotation: 0;

        Image {
            id: mazakodron;
            x: -0.435*paper.width;
            y: -0.27*paper.height;
            width: 0.8825*paper.width;
            height: 0.5505*paper.height;
            source: "mazakodron.png";
            asynchronous: true;
            smooth: true;
        }

        Image {

          id: mazak_img;
          x: -0.036*paper.width;
          y: -0.052*paper.height-(0.12*paper.height);
          width: 0.064*paper.width+(0.01*paper.width);
          height: 0.11*paper.height+(0.01*paper.width);
          source: "mazak.png";
          asynchronous: true;
          smooth: true;

          states: State {
            name: "down"; when: mazak_down == true;
            PropertyChanges {
              target: mazak_img;
              x: -0.036*paper.width;
              y: -0.052*paper.height;
              width: 0.064*paper.width;
              height: 0.11*paper.height;
            }
          }

          transitions: Transition {
            from: ""; to: "down"; reversible: true;
            SequentialAnimation {
              NumberAnimation { target: mazak_img; properties: "x,y,width,height"; duration: 100; easing.type:Easing.InQuad; }
            }
          }

        }

      }

    }

}
