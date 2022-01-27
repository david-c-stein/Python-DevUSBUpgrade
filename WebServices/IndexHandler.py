
import tornado.web
import uuid


class IndexHandler(tornado.web.RequestHandler):

    def __getstate__(self):
        # Process safe logger copy
        d = self.__dict__.copy()
        if 'logger' in d:
            d['logger'] = d['logger'].name
        return d

    def __setstate__(self, d):
        # Process safe logger copy
        if 'logger' in d:
            logging.config.dictConfig(d['logconfig'])
            d['logger'] = logging.getLogger(d['logger'])
        self.__dict__.update(d)

    def initialize(self, logger, logconfig, address, port):
        self.logger = logger
        self.logconfig = logconfig
        self.address = address
        self.port = port

    @tornado.web.asynchronous
    def get(self):
        '''
            Initial webpage with websocket injectables
            -- any contect changes belong in WSHandler/ContentBuilder
        '''

        title = 'Automation'
        css = '<link rel="stylesheet" href="static/assets/css/skelBase.css" /><link rel="stylesheet" href="static/assets/css/font-awesome.min.css" />'

        self.write( """
        <!DOCTYPE html>
        <html>
            <head id="head">
                <title>""" + title + """</title>
                <meta charset="utf-8" />
                """ + css + """
            </head>
            <body id="body">
                <noscript>
                    <div class='enableJS'>You need to enable javascript</div>
                </noscript>
                <script src="static/assets/js/jquery-3.1.0.min.js"></script>
                <script src="static/assets/js/skel.min.js"></script>
                <script src="static/assets/js/kinetic-v5.1.0.min.js"></script>
                <!-- #console--  <script src="static/assets/js/console.js"></script> -->
                <script src="static/assets/js/dropzone.js"></script>

            <!-- Header -->
                <header id="header">
                    <h1><a href="#">Automation</a></h1>
                    <a href="#login">Login</a>
                    <a href="#nav">Menu</a>
                </header>

            <!-- Login -->
                <login id="login">
                    <ul class="actions vertical">
                        <li><h3>Login to assume control</h3></li>
                        <li><label><b>Username</b></label></li>
                        <li><input type="text" placeholder="Enter Username" id="un" required></li>
                        <li><label><b>Password</b></label></li>
                        <li><input type="password" placeholder="Enter Password" id="pw" required></li>
                        <li><a id="loginButton" onclick="login()" href="#" class="button special fit">Login</a></li>
                    </ul>
                </login>

            <!-- Nav -->
                <nav id="nav">
                    <ul class="links">
                        <li><a href="#top">Top</a></li>
                        <li><a href="#content">Content</a></li>
                        <li><a href="#elements">Elements</a></li>
                        <li><a href="#grid">Grid System</a></li>
                    </ul>
                    <ul class="actions vertical">
                        <li><a href="#" class="button special fit">Download</a></li>
                        <li><a href="#" class="button fit">Documentation</a></li>
                    </ul>
                </nav>

            <!-- Main -->
            
                <!-- Status bar -->
                <div id="status" style="border-radius: 10px; text-align: center; font-size: large; color: #FFFFFF; ">Disconnected - No Automation Processes Running</span></div>

                <!-- Message modal -->
                <div id="msgModal" class="modalWindow">
                    <div>
                        <div class="modalHeader" id="modelHeader">
                            <h2>Sample modal window</h2>
                            <a href="#close" title="Close" class="close">X</a>
                        </div>
                        <div class="modalContent" id="modelContent">
                            <p>Sample model windows</p>
                        </div>
                        <div class="modalFooter" id="modelFooter">
                            <a href="#cancel" title="Cancel" class="cancel">Cancel</a>
                            <p>David Stein : 2014</p>
                            <div class="clear"></div>
                        </div>
                    </div>
                </div>
                
                <!-- Main content -->
                <div id="main" class="container">

                    <div class="row">

                        <div class="1u 12u$(medium)">
                            <a onclick="toggleDivs()" class="button special fit small" title="For a description"><bold>Select</bold></a>
                        </div>

                        <div class="11u 12u$(medium)">

                            <!-- Control Elements -->
                            <div id="controls" style="display:block">
                                <!-- USB Buttons -->
                                <h4>Host USB select</h4>
                                <ul class="actions fit small">
                                    <li><a onclick="window.btnPressed('usbHostDUT', 'btnPressed')" id="usbHostDUT" class="button fit small disabled" title="DUT usb port for testing">DUT Port</a></li>
                                    <li><a onclick="window.btnPressed('usbHostPC', 'btnPressed')" id="usbHostPC" class="button fit small disabled" title="PC usb port for imaging">PC Port</a></li>
                                </ul>

                                <h4>Client USB select</h4>
                                <ul class="actions fit small">
                                    <li><a onclick="window.btnPressed('usbClientMulti', 'btnPressed')" id="usbClientMulti" class="button fit disabled" title="Toggle Single or Multi Modes">Multi</a></li>
                                    <li><a onclick="window.btnPressed('usbClientP1', 'btnPressed')" id="usbClientP1" class="button fit small disabled">Port 1</a></li>
                                    <li><a onclick="window.btnPressed('usbClientP2', 'btnPressed')" id="usbClientP2" class="button fit small disabled">Port 2</a></li>
                                    <li><a onclick="window.btnPressed('usbClientP3', 'btnPressed')" id="usbClientP3" class="button fit small disabled">Port 3</a></li>
                                    <li><a onclick="window.btnPressed('usbClientP4', 'btnPressed')" id="usbClientP4" class="button fit small disabled">Port 4</a></li>
                                </ul>

                                <h4>Ethernet</h4>
                                <ul class="actions fit small">
                                    <li><a onclick="window.btnPressed('dutEthernet', 'btnPressed')" id="dutEthernet" class="button fit disabled" title="Press to Enable/Disable Ethernet">DUT Ethernet</a></li>
                                    <li><a onclick="window.btnPressed('dutWiu', 'btnPressed')" id="dutWiu" class="button fit disabled" title="Press to Enable/Disable WIU">DUT WIU</a></li>
                                </ul>

                                <h4>Power DUT</h4>
                                <ul class="actions fit small">
                                    <li><a onclick="window.btnPressed('dutPower', 'btnPressed')" id="dutPower" class="button fit disabled" title="Press to Enable/Disable Power">DUT Power</a></li>
                                </ul>
                            </div>

                            <!-- Information Text Stuffs -->
                            <div id="info" style="display:none">
                                <h4>USB / Power</h4>
                                This innterface is used to control the USB interfaces and Power for this system.
                                <ul>
                                    <li>Pressing Buttons on device</li>
                                    <li>Using this web interface</li>
                                </ul>
                            </div>

                            <!-- Camera Calibration Stuffs -->
                            <div id="camera" style="display:none">
                                <h4>Camera Event Modeling</h4>
                                <ul class="actions fit small">
                                    <li><a onclick="newImageCamera()" id="newimage" class="button fit small" title="new image">New Image</a></li>
                                </ul>
                                <div class="row 200%">
                                    <div class="12u 12u$(medium)">
                                        <div id="container" width="320", height="240" style="width:604px; height:404px; border:2px solid black;"></div>
                                    </div>
                                </div>
                            </div>

                            <!-- File Upload Stuffs -->
                            <div id="fileUpload" style="display:none">
                                <h4>File Upload</h4>
                                <div class="row 40%">
                                    <form action="/file-upload" class="dropzone" id="mydropzone"></form>
                                </div>
                            </div>
                            
                            
                            <!-- Serial Console Stuffs -->
                            <!-- #console--  
                            <div id="serialConsole" class="11u 12u$(medium)" style="display:none">
                                <h4>Serial Console</h4>
                                <canvas id="serialScreen">You're browser does not support HTML5.</canvas>
                            </div>
                            -->

                        </div>
                    </div>
                </div>

            <!-- Footer -->
                <footer id="footer">
                    <div class="container">
                        <div class="row double">
                            <div class="6u 12u$(medium)">
                                <h4>Test Automation</h4>
                                <p>Test Automation Goodness<br/>Contact me if you experience any issues with this application. </p>
                            </div>
                        </div>
                    </div>
                    <div class="copyright">
                        David Stein : 2015
                    </div>
                </footer>

                <!---------------------------------------------->

                <script src="static/assets/js/skelBase.js"></script>
                <script type="text/javascript" id="wsScript">

                    var socket;

                    function btnPressed(event_name, event_data) {
                        if (iAmInControl == true) {
                            window.sendMsg(event_name, event_data)
                        } else {
                            var e = document.getElementById("status");
                            e.classList.add('flash');
                            setTimeout(function() {
                                e.classList.remove('flash');
                            }, 500);
                        }
                    }

                    function sendMsg(event_name, event_data) {
                        if(socket) {
                            socket.send(event_name, event_data);
                        }
                    }

                    window.onload = function() {

                        var websocket = false;

                        if("WebSocket" in window) {
                            websocket = true;
                        } else {
                            console.log("WebSocket are not supported by this browser");
                        }

                        var mySocket = function() {
                            var ws;
                            var callbacks = {};

                            try {
                                // ensure only one connection is open
                                if(ws !== undefined && ws.readyState !== ws.CLOSED) {
                                    console.log("WebSocket is already open");
                                    return;
                                }
                                // c an instance of the websocket
                                ws = new WebSocket("ws://""" + self.address + """:""" + str(self.port) + """/ws/");
                            }
                            catch(e) {
                                console.log(e.message);
                            };

                            this.bind = function(event_name, callback) {
                                callbacks[event_name] = callbacks[event_name] || [];
                                callbacks[event_name].push(callback);
                                return this;            // chainable
                            };

                            this.unbind = function(event_name) {
                                delete callbacks[event_name];
                            };

                            this.send = function(event_name, event_data) {
                                var payload = JSON.stringify({event: event_name, data:event_data});
                                waitForSocket(ws, function(){
                                    ws.send(payload);
                                });
                                return this;
                            };

                            function waitForSocket(socket, callback) {
                                setTimeout(
                                    function () {
                                        if (socket.readyState === socket.OPEN) {
                                            // connection is ready
                                            if(callback != null)
                                                callback();
                                            return;
                                        } else {
                                            // connection is not ready yet
                                            waitForSocket(socket, callback)
                                        }
                                   }, 5);  // wait 5 milliseconds for connection
                            };

                            ws.onmessage = function(env) {
                                var j = JSON.parse(env.data);
                                dispatch(j[0], j[1]);
                            };

                            ws.onclose = function() {
                                dispatch('closed', null);
                                disableAll();
                            }

                            ws.onopen = function() {
                                dispatch('opened', null);
                            }

                            ws.onerror = function(evt) {
                                var err = evt.data;
                                console.log("Error occured");
                                dispatch('error', err);
                                disableAll();
                            };

                            var dispatch = function(event_name, message) {
                                var chain = callbacks[event_name];
                                if (typeof chain == 'undefined')
                                    return;             // no callbacks for this event
                                for(var i = 0; i < chain.length; i++)
                                    chain[i](message);
                            }
                        };

                        //-------------------------------------------------

                        if (websocket == true) {

                            socket = new mySocket();

                            socket.bind('opened', function(env) {
                                updateStatus(stateEnum.CONNECTED);
                            })

                            socket.bind('closed', function(env) {
                                updateStatus(stateEnum.DISCONNECTED);
                            })

                            socket.bind('error', function(env) {
                                updateStatus(stateEnum.ERROR);
                            })

                            socket.bind('contStatus', function(data) {
                                // control status from server
                                
                            })
                            
                            socket.bind( 'stateUpdate', function(data) {
                                // state information from server

                                for(var key in data) {
                                    if( key == 'control' ){
                                        if (data[key]) {
                                            updateStatus(stateEnum.CONTROL);
                                        } else {
                                            updateStatus(stateEnum.CONNECTED);
                                        }
                                    } else {
                                        // update button
                                        var x = document.getElementById( key );
                                        x.classList.remove('disabled', 'special');
                                        if (data[key] == true){
                                            x.classList.add('special');
                                        } else {
                                            x.classList.remove('special');
                                        }
                                    }
                                }
                            })

                            socket.bind('calibPos', function(data) {
                                // received calibration position information
                                updateRegionGroup(data);
                            })

                            socket.bind( 'calibrationImage', function(data) {
                                // received calibration image from server
                                runCalibrateCamera("data:image/png;base64," + data );
                            })


                            socket.bind( 'alert', function(data) {
                            
                                console.log("ALERT from server");
                            
                                // recieved message from server to be displayed to the client
                                var hdr = document.getElementById('modelHeader');
                                var bdy = document.getElementById('modelContent');
                                var ftr = document.getElementById('modelFooter');
                                // clear revious stuffs
                                hdr.innerHTML = "";
                                bdy.innerHTML = "";
                                ftr.innerHTML = "";
                                // populate new stuffs
                                hdr.innerHTML = '<h2>' +  data['hdr'] + '</h2><a href="#close" title="Close" class="close">X</a>';
                                bdy.innerHTML = '<p>' + data['hdr'] + '</p> <p>' + data['bdy'] + '</p>';
                                var f = '';
                                if(data['ftr'] == 'Ok') {
                                    f += '<a href="#ok" title="Ok" class="ok">Ok</a>';
                                }
                                else if(data['ftr'] == 'Cancel') {
                                    f += '<a href="#cancel" title="Cancel" class="cancel">Cancel</a>';
                                }
                                else if(data['ftr'] == 'Force') {
                                    f += '<a href="#ok" onclick="forceLogin()" title="Force" class="ok">Force</a>';
                                }
                                f += '<p>For issues contact David Stein</p>';
                                ftr.innerHTML = f;

                                window.location.hash = '#msgModal';
                            })

                        };
                    }

                    var stateEnum = Object.freeze({ UNKNOWN: 0, DISCONNECTED: 1, CONNECTED: 2, CONTROL: 3, ERROR: 4 });
                    var iAmInControl = false;

                    function login() {
                        var x1 = document.getElementById('un').value;
                        var x2 = document.getElementById('pw').value;
                        window.sendMsg('login', [ x1, x2 ]);
                    }

                    function forceLogin() {
                        window.sendMsg('forceLogin');
                    }

                    function clearPW() {
                        document.getElementById('psw').value = "";
                    }

                    function toggleDivs() {
                        var x1 = document.getElementById('controls');
                        var x2 = document.getElementById('camera');
                        var x3 = document.getElementById('info');
                        
                        /* //console--  
                        var x4 = document.getElementById('serialConsole');
                        if (x4.style.display === 'block') {
                            x1.style.display = 'block';
                            x2.style.display = 'none';
                            x3.style.display = 'none';
                            x4.style.display = 'none';
                        } else if (x1.style.display === 'block') {
                            x1.style.display = 'none';
                            x2.style.display = 'block';
                            x3.style.display = 'none';
                            x4.style.display = 'none';
                        } else if (x2.style.display === 'block') {
                            x1.style.display = 'none';
                            x2.style.display = 'none';
                            x3.style.display = 'block';
                            x4.style.display = 'none';
                        } else {
                            x1.style.display = 'none';
                            x2.style.display = 'none';
                            x3.style.display = 'none';
                            x4.style.display = 'block';
                        }
                        */
                        
                        if (x1.style.display === 'block') {
                            x1.style.display = 'none';
                            x2.style.display = 'block';
                            x3.style.display = 'none';
                        } else if (x2.style.display === 'block') {
                            x1.style.display = 'none';
                            x2.style.display = 'none';
                            x3.style.display = 'block';
                        } else {
                            x1.style.display = 'block';
                            x2.style.display = 'none';
                            x3.style.display = 'none';
                        }

                    }

                    function disableAll() {
                        disableAllButtons();
                    }

                    function disableAllButtons() {
                        l = [ 'usbHostDUT',
                              'usbHostPC',
                              'usbClientMulti',
                              'usbClientP1',
                              'usbClientP2',
                              'usbClientP3',
                              'usbClientP4',
                              'dutEthernet',
                              'dutWiu',
                              'dutPower'
                            ];

                        for( var i in l ) {
                            document.getElementById( l[i] ).classList.add('disabled');
                        }
                    }

                    function updateStatus( state ) {
                        var e = document.getElementById("status");

                        iAmInControl = false;

                        if (state == stateEnum.CONNECTED) {
                            e.innerHTML = "Connected - Not Logged In";
                            e.style.backgroundColor = 'darkblue';
                        }
                        else if (state == stateEnum.DISCONNECTED) {
                            e.style.backgroundColor = 'gray';
                            e.innerHTML = "Not connected";
                            window.disableAll();
                        }
                        else if (state == stateEnum.ERROR) {
                            e.style.backgroundColor = 'red';
                            e.innerHTML = "Not connected - An error has occured";
                            window.disableAll();
                        }
                        else if (state == stateEnum.CONTROL ) {
                            e.style.backgroundColor = 'green';
                            e.innerHTML = "In Control";
                            iAmInControl = true;
                        }
                        else {
                            e.style.backgroundColor = 'red';
                            e.innerHTML = "Hmmm. Something unknown has happened here";
                            window.disableAll();
                        }
                    }

                    //===========================================================================

                    // define stage
                    stage = new Kinetic.Stage({
                        container: 'container',
                        width: 600,
                        height: 400
                    });

                    function initStage(cameraImage) {

                        // define stage
                        stage = new Kinetic.Stage({
                            container: 'container',
                            width: 600,
                            height: 400
                        });

                        // background image
                        var bgImage = new Image();
                        bgImage.src = cameraImage
                        var backgroundImage = new Kinetic.Image({
                            x: 0,
                            y: 0,
                            image: bgImage,
                            width: 600,
                            height: 400
                        });
                        var background_layer = new Kinetic.Layer();
                        background_layer.add(backgroundImage);
                        stage.add(background_layer);

                        var eventRegions = ['PWR', 'HTH', 'CPU', 'VLT', 'TMP', 'AUX'];

                        for (var i = 0, len = eventRegions.length; i < len; i++) {
                            var layer = new Kinetic.Layer();
                            layer.add( addRegion('region' + (i+1), eventRegions[i]) );
                            stage.add(layer);
                        }
                        stage.draw();
                    }


                    function calibrateCamera() {
                        // server ship image
                        window.btnPressed('getCalibrationImage', 'btnPressed')
                    }

                    function newImageCamera() {
                        // server take new image
                        window.btnPressed('newCalibrationImage', 'btnPressed')
                        // server ship image
                        window.btnPressed('getCalibrationImage', 'btnPressed')
                    }

                    function runCalibrateCamera( cameraImage ) {
                        var e2 = document.getElementById("newimage");
                        e2.classList.add('special');
                        initStage(cameraImage);
                    }

                    function update(activeAnchor) {

                        var group = activeAnchor.getParent();

                        var topLeft = group.find('.topLeft')[0];
                        var topRight = group.find('.topRight')[0];
                        var bottomRight = group.find('.bottomRight')[0];
                        var bottomLeft = group.find('.bottomLeft')[0];
                        var image = group.find('.image')[0];

                        var anchorX = activeAnchor.x();
                        var anchorY = activeAnchor.y();

                        // update anchor positions
                        switch (activeAnchor.name()) {
                            case 'topLeft':
                                topRight.y(anchorY);
                                bottomLeft.x(anchorX);
                                break;
                            case 'topRight':
                                topLeft.y(anchorY);
                                bottomRight.x(anchorX);
                                break;
                            case 'bottomRight':
                                bottomLeft.y(anchorY);
                                topRight.x(anchorX);
                                break;
                            case 'bottomLeft':
                                bottomRight.y(anchorY);
                                topLeft.x(anchorX);
                                break;
                        }

                        image.setPosition(topLeft.getPosition());

                        var width = topRight.x() - topLeft.x();
                        var height = bottomLeft.y() - topLeft.y();
                        if(width && height) {
                            image.setSize({width:width, height:height});
                        }
                    }


                    function addAnchor(group, x, y, name) {

                        var anchor = new Kinetic.Circle({
                            x: x,
                            y: y,
                            stroke: '#555',
                            fill: '#ccc',
                            strokeWidth: 1,
                            radius: 3,
                            name: name,
                            draggable: true,
                            dragOnTop: false
                        });

                        anchor.on('dragmove', function() {
                            if (iAmInControl) {
                                var layer = this.getLayer();
                                update(this);
                                layer.draw();
                            }
                        });

                        anchor.on('mousedown touchstart', function() {
                            if (iAmInControl) {
                                group.setDraggable(false);
                                this.moveToTop();
                            }
                        });

                        anchor.on('dragend', function() {
                            if (iAmInControl) {
                                var layer = this.getLayer();
                                group.setDraggable(true);
                                layer.draw();
                            }
                        });

                        // add hover styling
                        anchor.on('mouseover', function() {
                            if (iAmInControl) {
                                var layer = this.getLayer();
                                document.body.style.cursor = 'pointer';
                                this.setStrokeWidth(3);
                                layer.draw();
                            }
                        });

                        anchor.on('mouseout', function() {
                            if (iAmInControl) {
                                var layer = this.getLayer();
                                document.body.style.cursor = 'default';
                                this.strokeWidth(1);
                                layer.draw();
                            }
                        });

                        group.add(anchor);
                    }


                    function updateRegionGroup(data) {

                        var regionName = data[0];
                        var x = data[1];
                        var y = data[2];
                        var offsetX = data[3];
                        var offsetY = data[4];
                        var rotation = data[5];
                        var skewX = data[6];
                        var skewY = data[7];

                        var topLeftX = data[8];
                        var topLeftY = data[9];
                        var topRightX = data[10];
                        var topRightY = data[11];
                        var bottomLeftX = data[12];
                        var bottomLeftY = data[13];
                        var bottomRightX = data[14];
                        var bottomRightY = data[15];

                        var groups = stage.find('Group');
                        for (var i = 0; i < groups.length; i++) {
                            if (groups[i].attrs.name == regionName) {
                                var group = groups[i];

                                var topLeft = group.find('.topLeft')[0];
                                var topRight = group.find('.topRight')[0];
                                var bottomLeft = group.find('.bottomLeft')[0];
                                var bottomRight = group.find('.bottomRight')[0];
                                var image = group.find('.image')[0];


                                group.setX(x);
                                group.setY(y);
                                group.setOffsetX(offsetX);
                                group.setOffsetY(offsetY);
                                group.setRotation(rotation);
                                group.setSkewX(skewX);
                                group.setSkewY(skewY);

                                topLeft.setX(topLeftX);
                                topLeft.setY(topLeftY);
                                topRight.setX(topRightX);
                                topRight.setY(topRightY);
                                bottomLeft.setX(bottomLeftX);
                                bottomLeft.setY(bottomLeftY);
                                bottomRight.setX(bottomRightX);
                                bottomRight.setY(bottomRightY);

                                image.setPosition(topLeft.getPosition());

                                var width = topRight.x() - topLeft.x();
                                var height = bottomLeft.y() - topLeft.y();
                                if(width && height) {
                                    image.setSize({width:width, height:height});
                                }

                                stage.draw();
                            }
                        }
                    }

                    function addRegion(region, name) {

                        var regionGroup = new Kinetic.Group({ name: region, x: 10, y: 10, draggable: false });

                        var regionInitialSize = { x: 0, y: 0, w: 40, h: 25 };

                        var img = new Image();
                        // base64 of a suitable transparent image
                        img.src = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAPCAYAAADkmO9VAAAABGdBTUEAALGPC/xhBQAAAAlwSFlzAAAOwgAADsIBFShKgAAAABl0RVh0U29mdHdhcmUAcGFpbnQubmV0IDQuMC4xMkMEa+wAAAAzSURBVDhPrcgxAQAgAAQh+5d+CzB5DiycbV8xC2bBLJgFs2AWzIJZMAtmwSyYBbNgvtu5p/6AqvhEI7kAAAAASUVORK5CYII=';

                        var boxStatusColor = "Black"

                        // region transparent image
                        var regionImg = new Kinetic.Image({
                            x: regionInitialSize.x,
                            y: regionInitialSize.y,
                            image: img,
                            width: regionInitialSize.w,
                            height: regionInitialSize.h,
                            name: 'image',
                            stroke: boxStatusColor,
                            strokeWidth:1 });


                        // add hover styling
                        regionImg.on('mouseover', function() {
                            if (iAmInControl) {
                                document.body.style.cursor = 'pointer';
                                this.setStrokeWidth(2);
                                this.draw();
                            }
                        });

                        regionImg.on('mouseout', function() {
                            if (iAmInControl) {
                                document.body.style.cursor = 'default';
                                this.strokeWidth(1);
                                this.draw();
                            }
                        });

                        regionGroup.add(regionImg);

                        var simpleText = new Kinetic.Text({
                            x: regionInitialSize.x ,
                            y: regionInitialSize.y + regionInitialSize.w,
                            text: name,
                            fontSize: 14,
                            fontFamily: 'Calibri',
                            width: regionInitialSize.w,
                            name: 'text',
                            align: 'center',
                            fill: 'black'
                        });

                        regionGroup.add(simpleText);

                        addAnchor(regionGroup, regionInitialSize.x, regionInitialSize.y, 'topLeft');
                        addAnchor(regionGroup, regionInitialSize.w, regionInitialSize.y, 'topRight');
                        addAnchor(regionGroup, regionInitialSize.w, regionInitialSize.h, 'bottomRight');
                        addAnchor(regionGroup, regionInitialSize.x, regionInitialSize.h, 'bottomLeft');



                        regionGroup.on('dragmove', function() {
                            if (iAmInControl) {
                                this.setDraggable(true);
                                update(this);
                                this.draw();
                            }
                        });

                        regionGroup.on('mousedown touchstart', function() {
                            if (iAmInControl) {
                                this.setDraggable(true);
                                this.moveToTop();
                            }
                        });

                        regionGroup.on('dragend', function() {

                            if (iAmInControl) {

                                this.setDraggable(true);
                                this.draw();

                                var topLeft = regionGroup.find('.topLeft')[0];
                                var topRight = regionGroup.find('.topRight')[0];
                                var bottomLeft = regionGroup.find('.bottomLeft')[0];
                                var bottomRight = regionGroup.find('.bottomRight')[0];
                                var image = regionGroup.find('.image')[0];

                                // send region data to server
                                window.sendMsg('calibPos', [
                                        regionGroup.attrs.name,
                                        regionGroup.attrs.x,
                                        regionGroup.attrs.y,
                                        regionGroup.attrs.offsetX,
                                        regionGroup.attrs.offsetY,
                                        regionGroup.attrs.rotation,
                                        regionGroup.attrs.skewX,
                                        regionGroup.attrs.skewY,

                                        topLeft.attrs.x,
                                        topLeft.attrs.y,
                                        topRight.attrs.x,
                                        topRight.attrs.y,
                                        bottomLeft.attrs.x,
                                        bottomLeft.attrs.y,
                                        bottomRight.attrs.x,
                                        bottomRight.attrs.y,
                                ]);
                            }
                        });

                        // add hover styling
                        regionGroup.on('mouseover', function() {
                            if (iAmInControl) {
                                this.setDraggable(true);
                                document.body.style.cursor = 'pointer';
                                this.draw();
                            }
                        });

                        regionGroup.on('mouseout', function() {
                            if (iAmInControl) {
                                document.body.style.cursor = 'default';
                                this.draw();
                            }
                        });

                        return regionGroup;
                    }

                </script>
            </body>
        </html>
        """)

        self.finish()

    def write_error(self, status_code, **kwargs):
        self.write("Gosh darnit, user! You caused a %d error." % status_code)

