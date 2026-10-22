// Disposable native control for the detached debugger experiment only.
// It makes progress observable through inherited redirected stdout and creates no children.
using System;
using System.IO;
using System.Text;
using System.Threading;

public static class WindowsStartupControl
{
    public static int Main(string[] args)
    {
        if (args.Length != 1) return 2;
        using (Stream output = Console.OpenStandardOutput())
        {
            if (args[0] == "deadline")
            {
                byte[] marker = Encoding.ASCII.GetBytes("deadline-ready\n");
                output.Write(marker, 0, marker.Length);
                output.Flush();
                Thread.Sleep(30000);
                return 0;
            }
            if (args[0] == "output-limit")
            {
                byte[] block = new byte[4096];
                for (int i = 0; i < block.Length; i++) block[i] = (byte)'x';
                for (int i = 0; i < 1024; i++)
                {
                    output.Write(block, 0, block.Length);
                    output.Flush();
                }
                Thread.Sleep(30000);
                return 0;
            }
        }
        return 2;
    }
}
