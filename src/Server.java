import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Scanner;

public class Server {

    public static void main(String[] args) {
        ServerSocket server;
        Socket client;

        try {
            server = new ServerSocket(8888);
            System.out.println("Connection established for the server side");
            client  = server.accept();
            while(true){
                InputStreamReader in = new InputStreamReader(client.getInputStream());
                BufferedReader br = new BufferedReader(in);

                PrintWriter print = new PrintWriter(client.getOutputStream());

                String dataIn = br.readLine();
                System.out.println("Received data: " + dataIn);

                Scanner sc = new Scanner(System.in);

                System.out.println("Send to server");
                String send = sc.nextLine();

                print.println(send);
                print.flush();

            }

        }catch (IOException ex){
            System.err.println(ex);
        }


    }
}
