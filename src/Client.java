import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.Scanner;

public class Client {

    public static void main(String[] args) {
        Socket client;

        try {
            while (true) {
                client = new Socket("localhost", 8888);
                System.out.println("Connection established with server");
                InputStreamReader in = new InputStreamReader(client.getInputStream());
                BufferedReader br = new BufferedReader(in);

                PrintWriter print = new PrintWriter(client.getOutputStream());

                System.out.println("Send to server");
                Scanner sc = new Scanner(System.in);

                print.println(sc.nextLine());
                print.flush();

                System.out.println("Received data:" + br.readLine());
            }
        } catch(IOException ex){
            System.err.println(ex);
        }

    }
}
