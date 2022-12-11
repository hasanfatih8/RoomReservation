import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;

public class JavaClient {

    public static void main(String[] args) {

        Socket serverSocket;
        DataOutputStream dataOutputStream;
        try {
            serverSocket = new Socket("localhost", 1453);
            dataOutputStream = new DataOutputStream(serverSocket.getOutputStream());
            dataOutputStream.writeUTF("hello server");
            serverSocket.close();
        } catch (IOException ex) {
            System.err.println(ex);
        }

    }

}