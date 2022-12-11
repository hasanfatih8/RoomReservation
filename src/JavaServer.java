import java.io.DataInputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;

public class JavaServer {

    public static void main(String[] args) {

        ServerSocket serverSocket;
        Socket clientSocket;
        DataInputStream dataInputStream;
        String message;
        try {
            serverSocket = new ServerSocket(1453);
            clientSocket = serverSocket.accept();
            dataInputStream = new DataInputStream(clientSocket.getInputStream());
            message = dataInputStream.readUTF();
            System.out.println("Received message: " + message);
            serverSocket.close();
        } catch (IOException ex) {
            System.err.println(ex);
        }

    }

}