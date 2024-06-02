import { Editor } from "@monaco-editor/react"
import { useRef, useState, useEffect } from "react"
import axios from "axios"


function App() {

  const codeEditor = useRef()
  const [code, setCode] = useState('')
  const [result, setResult] = useState('Test your code, your results will appear here')
  const [isSuccess, setIsSuccess] = useState(true);

  const onLoad = (e: any) => {
    codeEditor.current = e
    e.focus()
  }

  const runCode = async () => {
    if (!code) return;
    try {
      setResult('Loading...')
      const response = await axios.post('http://127.0.0.1:8000/run_code', { code: code });
      console.log(response.data);
      if (response.data["status"] == 0) {
        setResult(`Code tested sucessfully:\n ${response.data["result"]}`)
        setIsSuccess(true)
      } else {
        setResult(`Errors testing code:\n ${response.data["result"]}`)
        setIsSuccess(false)
      }
    } catch (error) {
      console.error('Error testing code:', error);
      const errorMessage = error.response?.data?.detail || 'Unknown error occurred';
      setResult(`Error testing code:\n ${errorMessage}`);
      setIsSuccess(false)
    }
  }

  const submitCode = async () => {
    if (!code) return;
    try {
      setResult('Loading...')
      const response = await axios.post('http://127.0.0.1:8000/submit_code', { code: code });
      console.log(response.data);
      if (response.data["status"] == 0) {
        setResult(`Code tested and submitted sucessfully:\n ${response.data["result"]}`)
        setIsSuccess(true)
      } else {
        setResult(`Errors testing code:\n ${response.data["result"]}`)
        setIsSuccess(false)
      }
    } catch (error) {
      console.error('Error while submitting code:', error);
      const errorMessage = error.response?.data?.detail || 'Error while submitting code';
      setResult(`Error:\n ${errorMessage}`);
      setIsSuccess(false)
    }
  }

  useEffect(() => {
    const fetchCode = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:8000/get_latest_code');
            console.log(response)
            setCode(response.data["code"]); // Adjust according to your actual response structure
            setResult(`Latest Code Run:\n${response.data["result"]}`)
        } catch (err) {
            setResult('Submit or test some code to see results');
            console.error(err);
        }
    };

    fetchCode();
  }, []); // The empty array ensures this effect runs only once after the initial rendering

  return (
    <div className="p-4 space-y-4">
      <div className="flex justify-end space-x-2">
          <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600" onClick={runCode}>
              Test Code
          </button>
          <button className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600" onClick={submitCode}>
              Submit Code
          </button>
      </div>
      <div className="p-4 border rounded">
        <h1 className="py-2 text-black">
              Code Editor
        </h1>
        <Editor height="45vh" defaultLanguage="python" theme="vs-dark" defaultValue="#Insert code here!" value={code} onChange={
          (value) => setCode(value!)
        } onMount={onLoad}></Editor>
      </div>
      <h1 className="py-2 text-black">
                Result Output
        </h1>
      <div className="p-4 border rounded bg-gray-50">
        <textarea className={`${isSuccess ? 'text-green-500' : 'text-red-500'} w-full h-40`} value={result} />
      </div>
    </div>
  )
}

export default App
