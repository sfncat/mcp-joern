import java.lang
import io.shiftleft.codepropertygraph.Cpg
import io.shiftleft.codepropertygraph.cpgloading.CpgLoader
import io.shiftleft.codepropertygraph.generated.nodes._
import io.shiftleft.semanticcpg.language.*
import io.shiftleft.codepropertygraph.generated.nodes
import io.shiftleft.codepropertygraph.generated.PropertyNames
import io.joern.dataflowengineoss.language.*
import scala.jdk.CollectionConverters.*

implicit val resolver: ICallResolver = NoResolve
implicit val finder: NodeExtensionFinder = DefaultNodeExtensionFinder

import io.joern.joerncli.console.Joern.context
import scala.collection.mutable
import scala.reflect.ClassTag
import _root_.io.joern.console.*
import _root_.io.joern.joerncli.console.JoernConsole.*
import _root_.io.shiftleft.codepropertygraph.cpgloading.*
import _root_.io.shiftleft.codepropertygraph.generated.{help as _, *}
import _root_.io.shiftleft.codepropertygraph.generated.nodes.*
import _root_.io.joern.dataflowengineoss.language.*
import _root_.io.shiftleft.semanticcpg.language.*




var cpg: Cpg = null
def convertToLong(str: String): Long = {
    // 移除字符串末尾的'L'字符（如果存在）
    val cleanStr = if (str.endsWith("L")) str.dropRight(1) else str
    // 转换为Long
    cleanStr.toLong
  }

def get_method_info_by_id(id:Long): String = {
  /*Get the info of a method by its id
  
  @param id: The id of the method
  @return: The info of the method, including the full name, name, signature and id
  */
  val method = cpg.method.id(id).head
  s"method_full_name=${method.fullName}|method_name=${method.name}|method_signature=${method.signature}|method_id=${method.id}L"
}

def get_class_info_by_id(id:Long): String = {
  /*Get the info of a class by its id
  
  @param id: The id of the class
  @return: The info of the class, including the full name, name and id
  */
  val cls = cpg.typeDecl.id(id).head
  s"class_full_name=${cls.fullName}|class_name=${cls.name}|class_id=${cls.id}L"
}

def get_call_info_by_id(id:Long): String = {
  /*Get the info of a call by its id

  @param id: The id of the call 
  @return: The info of the call, including the code, line and id
  */
  import scala.util.Try
  val call = cpg.call.id(id).head
  val line = Try(call.lineNumber.map(_.toString).getOrElse("?")).getOrElse("?")
  s"call_code=${call.code}|call_line=${line}|call_id=${call.id}L"
}

def _get_classes(class_full_name: String, visited: mutable.Set[String] = mutable.Set()): List[nodes.TypeDecl] = {
    /*Retrieves a list of anonymous classes defined within a class

    @param cpg: The CPG to query
    @param class_full_name: The fully qualified name of the class (e.g., com.android.nfc.NfcService)
    @return: List of full name and id of classes which are anonymous classes in the source class
    */
    if (visited.contains(class_full_name)) return List()
    val classDecl = cpg.typeDecl.filter(_.fullName == class_full_name).l.head
    var clsList:List[nodes.TypeDecl] = List(classDecl)
    val anonymous_lst = cpg.typeDecl.filter(_.filename == classDecl.filename).filter(_.fullName.startsWith(s"${class_full_name}" + "$")).l
    clsList = clsList ++ anonymous_lst
    visited.addAll(clsList.map(_.fullName))
    val sub_clsList = clsList.flatMap(cls => _get_classes(cls.fullName, visited))
    (clsList ++ sub_clsList).distinct
  }
def load_cpg(cpg_filepath: String) :Boolean = {
    /*
    Loads a CPG from a file if the cpg is not loaded or the cpg is not the same as the filepath
    
    @param cpg_filepath: The path to the CPG file, the filepath is absolute path
    @return: True if the CPG is loaded successfully, False otherwise
    */
    try{
      if (cpg == null) {
          println(s"Loading CPG from ${cpg_filepath}")
          cpg = CpgLoader.load(cpg_filepath)
          return true
      }else{
        val cur_cpg_filepath = get_cpg_filepath()

        if (cur_cpg_filepath != cpg_filepath) {
          println(s"Loading CPG from ${cpg_filepath} replace the old cpg")
          cpg = CpgLoader.load(cpg_filepath)
          return true
        }else{
          println(s"CPG already loaded from ${cpg_filepath}")
          return true
        }
      }
    
    }catch{
      case e: Exception => {
        println(s"Error loading CPG from ${cpg_filepath}: ${e.getMessage}")
        return false
      }
    }
  }
def get_cpg_filepath(): String = {
  /*Get the filepath of the CPG
  
  @return: The filepath of the CPG
  */
  try{
    cpg.graph.storagePathMaybe.getOrElse("").toString()
  }catch{
    case e: Exception => {
      println(s"Error getting CPG filepath: ${e.getMessage}")
      return ""
    }
  }
}
    
def get_method_callees(method_full_name: String): List[String] = {
  /*Get the callees of a method
  
  @param method_full_name: The fully qualified name of the source method(e.g., com.android.nfc.NfcService$6.onReceive:void(android.content.Context,android.content.Intent))
  @return: List of full name, name, signature and id of methods which call the source method
  */
  cpg.method.fullNameExact(method_full_name).headOption match {
    case Some(m) => m.callee.distinct.map(m => get_method_info_by_id(m.id)).l
    case None => List(s"ERROR: method not found: ${method_full_name}")
  }
}

def get_method_callers(method_full_name: String): List[String] = {
  /*Get the callees of a method
  
  @param method_full_name: The fully qualified name of the source method(e.g., com.android.nfc.NfcService$6.onReceive:void(android.content.Context,android.content.Intent))
  @return: List of full name, name, signature and id of methods called by the source method
  */
  cpg.method.fullNameExact(method_full_name).headOption match {
    case Some(m) => m.caller.distinct.map(m => get_method_info_by_id(m.id)).l
    case None => List(s"ERROR: method not found: ${method_full_name}")
  }
}

def get_class_full_name_by_id(id: String): String = {
  /*Get the fully name of a class by its id
  
  @param id: The id of the class
  @return: The fully name of the class
  */
  cpg.typeDecl.id(convertToLong(id)).head.fullName
}

def get_class_methods_by_class_full_name(class_full_name: String): List[String] = {
  /*Get the methods of a class by its fully qualified name
  
  @param class_full_name: The fully qualified name of the class
  @return: List of full name, name, signature and id of methods in the class
  */
  val cls_list = _get_classes(class_full_name)
  cls_list.flatMap{case cls: nodes.TypeDecl => cls.method.map(m => (s"methodFullName=${m.fullName} methodId=${m.id}L"))}
}  

def get_method_code_by_method_full_name(method_full_name: String): String = {
  /*Get the code of a method by its fully name
  
  @param method_full_name: The fully qualified name of the method
  @return: The code of the method
  */
  cpg.method.fullNameExact(method_full_name).headOption match {
    case Some(m) => m.code
    case None => s"ERROR: method not found: ${method_full_name}"
  }
}

def get_method_code_by_id(id: String): String = {
  /*Get the code of a method by its id
  
  @param id: The id of the method
  @return: The code of the method
  */
  cpg.method.id(convertToLong(id)).head.code
}

def get_method_full_name_by_id(id: String): String = {
  /*Get the fully qualified name of a method by its id
  
  @param id: The id of the method
  @return: The fully qualified name of the method
  */
  cpg.method.id(convertToLong(id)).head.fullName
}

def get_call_code_by_id(id: String): String = {
  /*Get the code of a call by its id
  
  @param id: The id of the call
  @return: The code of the call
  */
  cpg.call.id(convertToLong(id)).head.code
}

def get_method_code_by_class_full_name_and_method_name(class_full_name: String, method_name: String): List[String] = {
  /*Get the code of a method by its class full name and method name.
  Exact match first; falls back to case-insensitive substring match with a
  result cap (10) and explicit error messages when nothing is found.

  @param class_full_name: The fully qualified name of the class
  @param method_name: The name of the method (exact or substring)
  @return: List of method info strings, or an ERROR/INFO message
  */
  cpg.typeDecl.filter(_.fullName == class_full_name).headOption match {
    case None => List(s"ERROR: class not found: ${class_full_name}")
    case Some(td) =>
      val all = td.method.l
      val exact = all.filter(_.name == method_name)
      if (exact.nonEmpty) {
        exact.map(m => (s"methodFullName=${m.fullName} methodId=${m.id}L")).l
      } else {
        // Level 1: case-insensitive substring match
        val lname = method_name.toLowerCase
        val fuzzy = all.filter(_.name.toLowerCase.contains(lname))
        if (fuzzy.nonEmpty) {
          if (fuzzy.size <= 10) {
            fuzzy.map(m => (s"[fuzzy] methodFullName=${m.fullName} methodId=${m.id}L")).l
          } else {
            fuzzy.take(10).map(m => (s"[fuzzy] methodFullName=${m.fullName} methodId=${m.id}L")).l :+
              s"INFO: ${fuzzy.size} methods match '${method_name}', showing first 10. Use exact name for precise result."
          }
        } else {
          // Level 2: Levenshtein edit-distance fallback for typos (e.g. doSUexist -> doesSUexist)
          def levenshtein(a: String, b: String): Int = {
            val m = a.length; val n = b.length
            val dp = Array.ofDim[Int](m + 1, n + 1)
            for (i <- 0 to m) dp(i)(0) = i
            for (j <- 0 to n) dp(0)(j) = j
            for (i <- 1 to m; j <- 1 to n) {
              dp(i)(j) = math.min(
                math.min(dp(i-1)(j) + 1, dp(i)(j-1) + 1),
                dp(i-1)(j-1) + (if (a(i-1) == b(j-1)) 0 else 1)
              )
            }
            dp(m)(n)
          }
          val threshold = math.max(2, lname.length / 3)
          val close = all.map(m => (m, levenshtein(m.name.toLowerCase, lname)))
                       .filter { case (_, d) => d <= threshold }
                       .sortBy { case (_, d) => d }
                       .take(10)
          if (close.nonEmpty) {
            close.map { case (m, d) => s"[typo? dist=$d] methodFullName=${m.fullName} methodId=${m.id}L" }.l
          } else {
            List(s"ERROR: no method containing or similar to '${method_name}' in ${class_full_name}")
          }
        }
      }
  }
}

def get_method_by_full_name_without_signature(full_name_without_signature: String): List[String] = {
  /*Get the info of a method list by its fully qualified name without signature
  
  @param full_name_without_signature: The fully qualified name of the method without signature
  @return: The info of the methods, including the full name, name, signature and id
  */
  cpg.method.filter(_.fullName.contains(full_name_without_signature)).map(m => get_method_info_by_id(m.id)).l
}

def get_derived_classes_by_class_full_name(class_full_name: String): List[String] = {
  /*Get the derived classes of a class
  
  @param class_full_name: The fully qualified name of the class
  @return: The derived classes info of the class, including the full name, name and id
  */
  cpg.typeDecl.filter(_.fullName == class_full_name).headOption match {
    case Some(td) => td.derivedTypeDeclTransitive.map(c => get_class_info_by_id(c.id)).l
    case None => List(s"ERROR: class not found: ${class_full_name}")
  }
}

def get_parent_classes_by_class_full_name(class_full_name: String): List[String] = {
  /*Get the parent classes of a class
  
  @param class_full_name: The fully qualified name of the class
  @return: The parent classes info of the class, including the full name, name and id
  */
  val cls = cpg.typeDecl.filter(_.fullName == class_full_name).head
  cls.start.repeat(_.inheritsFromOut._refOut.head.asInstanceOf[TypeDecl])(_.until(_.filter(c => c.inheritsFromOut.isEmpty)).emit).map(c => get_class_info_by_id(c.id)).l
}

def get_method_by_call_id(id: String): String = {
  /*Get the method info by the call id which the call is in the method
  
  @param id: The id of the call
  @return: The method info of the call
  */
  get_method_info_by_id(cpg.call.id(convertToLong(id)).head.method.id)
}

def get_referenced_method_full_name_by_call_id(id: String): String = {
  /*Get the method info by the call id which the call is referenced the method
  
  @param id: The id of the call
  @return: The method info of the call
  */
  cpg.call.id(convertToLong(id)).head.methodFullName
}

def get_calls_in_method_by_method_full_name(method_full_name: String): List[String] = {
  /* Get the calls in a method by the method full name
  @param method_full_name: The fully qualified name of the method
  @return: The calls info in the method, including the code and id
   */
  cpg.method.filter(_.fullName == method_full_name).headOption match {
    case Some(method) => method.ast.isCall.collect(c => get_call_info_by_id(c.id)).l
    case None => List(s"ERROR: method not found: ${method_full_name}")
  }
}

// ===== Script version (used to detect mismatch between Python MCP and Joern script) =====
def get_script_version(): String = "1.1.0"

// ===== Dataflow analysis helper functions =====

def format_flow_step(node: nodes.StoredNode): String = {
  /*Serialize a single flow step node to a pipe-separated string.
  Double quotes are replaced with single quotes to avoid breaking Scala List serialization.

  @param node: A CPG node in a flow path
  @return: Formatted string with type, code, line and id fields
  */
  import scala.util.Try
  // PropertyNames constants were renamed in newer CPG versions (CODE -> Code, LINE_NUMBER -> LineNumber).
  // Resolve via reflection so server_tools.sc compiles against both old and new joern versions.
  val PN = io.shiftleft.codepropertygraph.generated.PropertyNames
  val codePropName: String = Try(PN.getClass.getMethod("Code").invoke(null).asInstanceOf[String])
    .getOrElse(Try(PN.getClass.getMethod("CODE").invoke(null).asInstanceOf[String]).getOrElse("CODE"))
  val linePropName: String = Try(PN.getClass.getMethod("LineNumber").invoke(null).asInstanceOf[String])
    .getOrElse(Try(PN.getClass.getMethod("LINE_NUMBER").invoke(null).asInstanceOf[String]).getOrElse("LINE_NUMBER"))
  val code = Try(node.property[String](codePropName)).getOrElse("")
    .replaceAll("[\n\r\t]", " ")
    .replace("\"", "'")
    .replace("|", "/")
  val line = Try(node.property[Integer](linePropName)).map(_.toString).getOrElse("?")
  s"type=${node.label}|code=${code}|line=${line}|id=${node.id}L"
}

def format_flow_path(flow: io.joern.dataflowengineoss.language.Path): String = {
  /*Serialize a complete flow path with steps joined by " --> ".

  @param flow: A dataflow path from source to sink
  @return: Formatted string with all steps
  */
  flow.elements.zipWithIndex.map { case (node, idx) =>
    s"step${idx}:(${format_flow_step(node)})"
  }.mkString(" --> ")
}

// ===== Dataflow query tool functions =====

def find_flows_from_method_params_to_sink_method(
  source_method_full_name: String,
  sink_method_full_name: String,
  max_paths: Int = 20
): List[String] = {
  /*Find taint flow paths from all parameters of a source method to calls of a sink method.

  @param source_method_full_name: Full name of the source method
  @param sink_method_full_name: Full name of the sink method (exact match)
  @param max_paths: Maximum number of flow paths to return
  @return: List of flow path strings
  */
  val source = cpg.method.fullNameExact(source_method_full_name).parameter
  val sink = cpg.call.methodFullNameExact(sink_method_full_name).argument
  sink.reachableByFlows(source).map(format_flow_path).take(max_paths).l
}

def find_flows_from_source_call_to_sink_call(
  source_call_name: String,
  sink_call_name: String,
  max_paths: Int = 20
): List[String] = {
  /*Find taint flow paths from calls named source_call_name to calls named sink_call_name.
  Uses simple name matching (covers all overloads).

  @param source_call_name: Simple method name of source call (e.g., getStringExtra)
  @param sink_call_name: Simple method name of sink call (e.g., exec)
  @param max_paths: Maximum number of flow paths to return
  @return: List of flow path strings
  */
  val source = cpg.call.name(source_call_name)
  val sink = cpg.call.name(sink_call_name).argument
  sink.reachableByFlows(source).map(format_flow_path).take(max_paths).l
}

def find_flows_from_param_index_to_sink_call(
  source_method_full_name: String,
  param_index: Int,
  sink_call_name: String,
  max_paths: Int = 20
): List[String] = {
  /*Find taint flow paths from a specific parameter (0-based index) to calls with a given name.

  @param source_method_full_name: Full name of the source method
  @param param_index: 0-based index of the parameter
  @param sink_call_name: Simple method name of the sink call
  @param max_paths: Maximum number of flow paths to return
  @return: List of flow path strings
  */
  val source = cpg.method.fullNameExact(source_method_full_name).parameter.index(param_index)
  val sink = cpg.call.name(sink_call_name).argument
  sink.reachableByFlows(source).map(format_flow_path).take(max_paths).l
}

