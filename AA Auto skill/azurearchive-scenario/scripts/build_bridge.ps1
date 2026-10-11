param(
    [Parameter(Mandatory=$true)][string]$AppDirectory,
    [string]$Output = (Join-Path $PSScriptRoot '..\assets\compiler\AAKit.CompilerBridge.dll')
)
$ErrorActionPreference='Stop'
# PowerShell 7 ships Roslyn. Use the application's .NET 6 references explicitly;
# Add-Type's implicit references would target the PowerShell runtime instead.
$AppDirectory=(Resolve-Path -LiteralPath $AppDirectory).Path
$refs=@(Get-ChildItem -LiteralPath (Join-Path $AppDirectory 'dotnet') -Filter '*.dll' -File | ForEach-Object {
    $file=[IO.File]::OpenRead($_.FullName)
    try {
        $reader=[Reflection.PortableExecutable.PEReader]::new($file)
        try { if($reader.HasMetadata) { $_.FullName } } finally { $reader.Dispose() }
    } finally { $file.Dispose() }
})
$refs+=@('BepInEx\core\BepInEx.Core.dll','BepInEx\core\BepInEx.Unity.IL2CPP.dll',
    'BepInEx\core\Il2CppInterop.Runtime.dll','BepInEx\interop\Il2Cppmscorlib.dll','BepInEx\interop\Il2CppSystem.dll',
    'BepInEx\interop\Newtonsoft.Json.dll','BepInEx\interop\Assembly-CSharp.dll',
    'BepInEx\interop\UnityEngine.CoreModule.dll') | ForEach-Object { Join-Path $AppDirectory $_ }
$metadataRefs=[Microsoft.CodeAnalysis.MetadataReference[]]@($refs | ForEach-Object {
    [Microsoft.CodeAnalysis.MetadataReference]::CreateFromFile($_)
})
$source=Join-Path $PSScriptRoot '..\assets\compiler\CompilerBridge.cs'
$tree=[Microsoft.CodeAnalysis.CSharp.CSharpSyntaxTree]::ParseText([IO.File]::ReadAllText($source))
$options=[Microsoft.CodeAnalysis.CSharp.CSharpCompilationOptions]::new([Microsoft.CodeAnalysis.OutputKind]::DynamicallyLinkedLibrary)
$compilation=[Microsoft.CodeAnalysis.CSharp.CSharpCompilation]::Create('AAKit.CompilerBridge',
    [Microsoft.CodeAnalysis.SyntaxTree[]]@($tree),$metadataRefs,$options)
$Output=[IO.Path]::GetFullPath($Output)
$stream=[IO.File]::Create($Output+'.tmp')
try { $result=$compilation.Emit($stream) } finally { $stream.Dispose() }
if(-not $result.Success) {
    $result.Diagnostics | ForEach-Object ToString | Write-Error
    throw 'Bridge compilation failed; existing binary was preserved.'
}
[IO.File]::Move($Output+'.tmp',$Output,$true)
Write-Output "Built $Output"
