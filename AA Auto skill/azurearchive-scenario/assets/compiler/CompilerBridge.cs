using System;
using System.IO;
using BepInEx;
using BepInEx.Unity.IL2CPP;
using AzureArchive.Automation;
using Newtonsoft.Json.Linq;

// Active only in a child process explicitly started by aa_tool.py.
[BepInPlugin("aa.kit.compiler.bridge", "AA Kit Compiler Bridge", "1.7.0")]
public sealed class CompilerBridge : BasePlugin
{
    public override void Load()
    {
        if (!String.IsNullOrEmpty(Environment.GetEnvironmentVariable("AA_KIT_NATIVE_JOB")))
            AddComponent<CompilerRunner>();
    }
}

public sealed class CompilerRunner : UnityEngine.MonoBehaviour
{
    public CompilerRunner(IntPtr pointer) : base(pointer) { }
    private bool finished;
    private float nextAttempt = 8f;
    public void Update()
    {
        if (finished || UnityEngine.Time.realtimeSinceStartup < nextAttempt) return;
        string jobPath = Environment.GetEnvironmentVariable("AA_KIT_NATIVE_JOB");
        if (String.IsNullOrEmpty(jobPath)) return;
        bool keepOpen = false;
        string response;
        try
        {
            JObject job = JObject.Parse(File.ReadAllText(jobPath));
            string command = job["command"].ToString();
            JObject result;
            if (command == "compile")
                result = AuthoringService.Execute("compile", job["args"].Cast<JObject>());
            else if (command == "schema")
                result = AuthoringApiSchema.GetSchema();
            else if (command == "play")
            {
                if (ScenarioResourceManager.Instance == null || !ScenarioResourceManager.Instance.AreDbsLoaded)
                {
                    if (UnityEngine.Time.realtimeSinceStartup >= 60f)
                        throw new InvalidOperationException("Player resource databases did not finish loading.");
                    nextAttempt = UnityEngine.Time.realtimeSinceStartup + 1f;
                    return;
                }
                if (AuthoringWorkbench.Instance == null) AuthoringWorkbench.Bootstrap();
                if (AuthoringWorkbench.Instance == null && UnityEngine.Time.realtimeSinceStartup < 60f)
                { nextAttempt = UnityEngine.Time.realtimeSinceStartup + 1f; return; }
                if (AuthoringWorkbench.Instance == null) throw new InvalidOperationException("Player workbench is unavailable.");
                string scenario = job["args"]["scenario"].ToString();
                AuthoringWorkbench.OpenScenario(scenario);
                result = JObject.Parse("{\"ok\":true,\"data\":{\"play_requested\":true},\"warnings\":[]}");
                keepOpen = true;
            }
            else throw new InvalidOperationException("Unsupported bridge command: " + command);
            JToken error = result["error"];
            string code = error == null || error["code"] == null ? "" : error["code"].ToString();
            if ((code == "RESOURCE_NOT_READY" || code == "CATALOG_NOT_READY" || code == "RESOURCE_BUSY")
                && UnityEngine.Time.realtimeSinceStartup < 60f)
            { nextAttempt = UnityEngine.Time.realtimeSinceStartup + 1f; return; }
            response = result.ToString();
        }
        catch (Exception ex)
        {
            // Serialize exception text as data, never as an executable command.
            JObject result = new JObject();
            result["ok"] = new JValue(false);
            JObject error = new JObject();
            error["code"] = new JValue("BRIDGE_EXCEPTION");
            error["message"] = new JValue(ex.ToString());
            result["error"] = error;
            response = result.ToString();
        }
        finished = true;
        string output = jobPath + ".response.json";
        File.WriteAllText(output + ".tmp", response);
        File.Move(output + ".tmp", output, true);
        if (!keepOpen) UnityEngine.Application.Quit();
    }
}
