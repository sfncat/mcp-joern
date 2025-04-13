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


def getAnonymousClasses(class_full_name: String): List[String] = {
    cpg.typeDecl
      .filter(_.filename == class_full_name)
      .filter(_.fullName.startsWith(s"${class_full_name}" + "$"))
      .map(c => (s"classFullName=$' + '{c.fullName} classId=${c.id}L")).l
  }