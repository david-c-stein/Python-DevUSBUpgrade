import java.net.URI;
import java.net.URISyntaxException;
import org.java_websocket.WebSocketImpl;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.drafts.Draft;
import org.java_websocket.drafts.Draft_10;
import org.java_websocket.framing.Framedata;
import org.java_websocket.handshake.ServerHandshake;
import org.json.JSONException;
import org.json.JSONObject;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;


public class WSClientConn {
	
	public static class WSClient {
		
		private WebSocketClient ws;
		private Map<String, List<Object>> callbacks = new HashMap<String, List<Object>>();
		
		public connect( String sUri ){
			try {
				uri = new URI( sUri );
		
				WebSocketImpl.DEBUG = true;
				ws = new WebSocketClient( new URI( uriField.getText() ), (Draft) draft.getSelectedItem() ) {

					@Override
					public void onMessage( String message ) {
						System.out.println( "received: " + message );
						JSONObject obj = new JSONObject(message);
						dispatch(obj.getString("event"), obj.getString("data"));
					}

					@Override
					public void onOpen( ServerHandshake handshake ) {
						String msg = "You are connected: " + getURI() + "\n";
						dispatch('opened', msg);
					}

					@Override
					public void onClose( int code, String reason, boolean remote ) {
						String msg = "You have been disconnected from: " + getURI() + "; Code: " + code + " " + reason + "\n";
						dispatch('closed', msg);
						connect.setEnabled( true );
						uriField.setEditable( true );
						draft.setEditable( true );
						close.setEnabled( false );
					}

					@Override
					public void onError( Exception ex ) {
						String msg = "Exception occured ...\n" + ex + "\n";
						dispatch('error', msg);
						ex.printStackTrace();
						connect.setEnabled( true );
						uriField.setEditable( true );
						draft.setEditable( true );
						close.setEnabled( false );
					}
					
					public void sendMsg( String eventName, String eventData ) {
						JSONObject payload = new JSONObject()
								.put("event", eventName)
								.put("data", eventData);
						send(payload.toString());
					}
					
					//----------------
					
					public void bind( String eventName, Object callback ) {
						if( !callbacks.containsKey(eventName) ) {
							callbacks.put(eventName, new ArrayList<Object>())
						}
						callbacks.put(eventName, callback);
					}
					
					public void unbind( String eventName ) {
						if( callbacks.containsKey(eventName) ) 
							callback.remove(eventName, callback)
					}
					
					public void dispatch( eventName, message ) {
						try {
							chain = callbacks.get(eventName);
							for(int i=0; i<(chain.length); i++) {
								chain[i](message);
							}
						} catch ( Exception e ) {
							System.out.println( "Call exception: " + e );
						}
					}
				};
				
				close.setEnabled( true );
				connect.setEnabled( false );
				uriField.setEditable( false );
				draft.setEditable( false );
				
				wc.connect();
				
			} catch ( URISyntaxException e ) {
				System.out.println( uriField.getText() + " is not a valid WebSocket URI\n" );
			}
			
		}

		public close(){
			wc.close();
		}
		
	}
	
	
	public static class ClientAutomation {
	
		private static final int UNKNOWN = 0;
		private static final int DISCONNECTED = 1;
		private static final int CONNECTED = 2;
		private static final int CONTROL = 3;
		private static final int ERROR = 4;
	
		private boolean iAmInControl = false;
		private boolean usbHostDUT = false;
		private boolean usbHostPC = false;
		private boolean usbClientMulti = false;
		private boolean usbClientP1 = false;
		private boolean usbClientP2 = false;
		private boolean usbClientP3 = false;
		private boolean usbClientP4 = false;
		private boolean dutEthernet = false;
		private boolean dutWiu = false;
		private boolean dutPower = false;
		private WSClient conn;
		
		// constructor
		public ClientAutomation() {
			;
		}
		
		// destructor
		protected void finalize() {
			if (conn != null){
				conn.close();
			}
			conn = null;
		}
		
		//---------
		
		public connect() {
			try{
				// connect to server
				conn = new WSClient();
				
				// connection event bindings
				conn.bind('opened', this.connected);
				conn.bind('closed', this.disconnected);
				conn.bind('error', this.error);
				
				// server bindings
				conn.bind('stateUpdate', this.stateUpdate);
				conn.bind('contStatus', this.contStatus);
				conn.bind('calibPos', this.calibPos);
				conn.bind('calibrationImage', this.alert);
				
				conn.connect("ws://127.0.0.1:8888/ws/");
				
			} catch ( Exception e ) {
				System.out.println( "Exception connecting to server" );
			}
		}

		public disconnect() {
			if( conn != null ) {
				conn.close();
			}
		}
		
		//---------
		
		public connected(String event) {
			this.updateStatus(CONNECTED);
		}
		
		public disconnected(String event) {
			this.updateStatus(DISCONNECTED);
		}

		public error(String event) {
			this.updateStatus(ERROR);
		}
		
		public updateStatus(int state){
			System.out.println("Comm state: " + state);
		}
		
		//---------

		public contStatus(data) {
			System.out.println(data);
		}
		
		public calibPos(data) {
			/* 
			  Calibration Position message
				regionName = data[0];
				x = data[1];
				y = data[2];
				offsetX = data[3];
				offsetY = data[4];
				rotation = data[5];
				skewX = data[6];
				skewY = data[7];

				topLeftX = data[8];
				topLeftY = data[9];
				topRightX = data[10];
				topRightY = data[11];
				bottomLeftX = data[12];
				bottomLeftY = data[13];
				bottomRightX = data[14];
				bottomRightY = data[15];
			*/
			
			JSONArray jsonArray = new JSONArray(data);
			List<String> list = new ArrayList<String>();
			for (int i=0; i<jsonArray.length(); i++) {
				list.add( jsonArray.getString(i) );
			}
		}
		
		public saveImage(data) {
			Path path = Paths.get("calibImg.png");
			Files.write(path, Base64.getDecoder().decode(data));
		}
		
		
		
		public class alertMsg {
			@JsonProperty("hdr")
			public String header;
			
			@JsonProperty("bdy")
			public String body;
			
			@JsonProperty("ftr")
			public String footer;
		}
		
		public alert(data){
			// ['alert', {'hdr':hdr, 'bdy':body, 'ftr':ftr}]
			alertMsg msg = mapper.readValue(data, alertMsg.class);
		}
		
		
		public class stateUpdateMsg {
			@JsonProperty("control")
			public boolean iAmInControl;
			
			@JsonProperty("usbHostDUT")
			public boolean usbHostDUT;
			
			@JsonProperty("usbHostPC")
			public boolean usbHostPC;
			
			@JsonProperty("usbClientMulti")
			public boolean usbClientMulti;
			
			@JsonProperty("usbClientP1")
			public boolean usbClientP1;
			
			@JsonProperty("usbClientP2")
			public boolean usbClientP2;
			
			@JsonProperty("usbClientP3")
			public boolean usbClientP3;
			
			@JsonProperty("usbClientP4")
			public boolean usbClientP4;
			
			@JsonProperty("dutEthernet")
			public boolean dutEthernet;
			
			@JsonProperty("dutWiu")
			public boolean dutWiu;
			
			@JsonProperty("dutPower")
			public boolean dutPower;
			
			@JsonProperty("conn")
			public int conn;
		}
		
		public stateUpdate(data) {
			stateUpdateMsg msg = mapper.readValue(data, stateUpdateMsg.class);
		}
		
		//---------

		public login(username, password){
			this.conn.sendMsg('login', new String[]{username, password});
		}
		
		public forceLogin() {
			this.conn.sendMsg('forceLogin', null);
		}
		
		public setUsbHostDUT() {
			this.conn.snedMsg('usbHostDUT', 'On');
		}
		
		public setUsbHostPC():
			this.conn.sendMsg('usbHostPC', 'On')
		
		public setUsbClientMulti(value):
			this.conn.sendMsg('usbClientMulti', value)
		
		public setUsbClientP1(value):
			this.conn.sendMsg('usbClientP1', value)
		
		public setUsbClientP2(value):
			this.conn.sendMsg('usbClientP2', value)

		public setUsbClientP3(value):
			this.conn.sendMsg('usbClientP3', value)

		public setUsbClientP4(value):
			this.conn.sendMsg('usbClientP4', value)

		public setDutEthernet(value):
			this.conn.sendMsg('dutEthernet', value)

		public setDutWiu(value):
			this.conn.sendMsg('dutWiu', value)

		public setDutPower(value):
			this.conn.sendMsg('dutPower', value)

		public setTstRun(value):
			this.conn.sendMsg('tstRun', value)
		
	}
	
	public sleep(int t) {
		Thread.currentThread().sleep(t * 1000);
	}
	
	
	
	public static void main (String args[]) {
		System.out.println("Example Automation Interface");
		WebSocketImpl.DEBUG = true;
		String uri = "ws://localhost:8888";
		ClientAutomation ca = new ClientAutomation();
		
		ca.connect(uri);
		this.sleep(4);
		
		ca.login('qa', 'test');
		this.sleep(2);
		
		ca.forceLogin()
		this.sleep(2)
    
		ca.setUsbHostDUT()
		this.sleep(1)
        
		ca.setUsbHostPC()
		this.sleep(1)

		String value = 'On'
		ca.setUsbClientMulti(value)
		this.sleep(1)
		ca.setUsbClientP1(value)
		this.sleep(1)
		ca.setUsbClientP2(value)
		this.sleep(1)
		ca.setUsbClientP3(value)
		this.sleep(1)
		ca.setUsbClientP4(value)
		this.sleep(1)

		value = 'Off'
		ca.setUsbClientMulti(value)
		this.sleep(1)
		ca.setUsbClientP1(value)
		this.sleep(1)
		ca.setUsbClientP2(value)
		this.sleep(1)
		ca.setUsbClientP3(value)
		this.sleep(1)
		ca.setUsbClientP4(value)
		this.sleep(1)
    
		value = 'On'
		ca.setUsbClientMulti(value)
		this.sleep(1)
		ca.setUsbClientP1(value)
		this.sleep(1)
		ca.setUsbClientP2(value)
		this.sleep(1)
		ca.setUsbClientP3(value)
		this.sleep(1)
		ca.setUsbClientP4(value)
		this.sleep(1)
    
   
		value = 'On'
		ca.setDutEthernet(value)
		this.sleep(1)
		ca.setDutWiu(value)
		this.sleep(1)
    
		value = 'Off'
		ca.setDutEthernet(value)
		this.sleep(1)
		ca.setDutWiu(value)
		this.sleep(1)

		ca.setDutPower('On')
		this.sleep(1)
		ca.setDutPower('Off')
		this.sleep(1)
		ca.setDutPower('On')
		this.sleep(1)
		ca.setDutPower('Off')
		this.sleep(1)

		ca.setTstRun('On')
		this.sleep(1)
		
		
		// stopping ws connection
		ca.disconnect();
	}	
	
}

