import os
import subprocess
import shutil
import re

dut_file = "/home1/inr16/learning/scripting/Counter"
dest_folder = "/home1/inr16/learning/scripting/Experiment/uvm_gen/count"
os.makedirs(dest_folder, exist_ok=True)  # ensure destination exists


all_file = [f for f in os.listdir(dut_file) if f.endswith(".sv")]
sv_files = [os.path.join(dut_file, f) for f in all_file]

search_words = ["module", "interface", "package"]

print(".sv files are : ")
for f in sv_files:
    print(f"\nFile: {f}")

    #print all occurrences of keywords
    for word in search_words:
        result = subprocess.getoutput(f'grep -n "{word}" "{f}"')
        if result:
            print(f"Found '{word}':")
            print(result)
    
    # Get first meaningful word (works even if no comment)
    cmd = f"grep -v '^[[:space:]]*//' '{f}' | grep -v '^$' | head -n 1 | awk '{{print $1}}'"
    first_word = subprocess.getoutput(cmd).strip()
    
    #To Copy DUT File 
    if first_word == "module":
        dest_file = os.path.join(dest_folder, os.path.basename(f))
        shutil.copy(f,dest_file)
   # elif first_word == "package":
        #dest_file = os.path.join(dest_folder, os.path.basename(f))
       # shutil.copy(f,dest_file)
    #elif first_word == "`include":
       # dest_file = os.path.join(dest_folder, os.path.basename(f))
       # shutil.copy(f,dest_file)
   # elif first_word == "interface":
       # dest_file = os.path.join(dest_folder, os.path.basename(f))
        #shutil.copy(f,dest_file)
        
    files = f
    
    cmd_inputs  = f"awk '/module /,/);/' {files} | grep -oP '\\binput\\b.*'"
    cmd_outputs = f"awk '/module /,/);/' {files} | grep -oP '\\boutput\\b.*'"
    raw_inputs = subprocess.getoutput(cmd_inputs).splitlines()
    raw_outputs = subprocess.getoutput(cmd_outputs).splitlines()
    
    print("Input Signals Before cleaning : ",raw_inputs)
    print("Output Signals Before cleaning : ",raw_outputs)
    
    #Enter class name
    intf = "counter_intf"
    class_seq = "counter_sequence_item"
    class_seqr = "counter_sequencer"
    class_seqn = "counter_sequence"
    class_drv ="counter_driver"
    class_mon ="counter_monitor"
    class_agt = "counter_agent"
    class_scr ="counter_scroreboard"
    class_env = "counter_env"
    class_tst = "counter_test"
    module_tb = "counter_top"
    freq = 10
    dut_name = "Up_Down_Counter" 
    
    def clean_signals(lines):
        #signals=[]
        #To remove data type or to get only signal name
#        for line in lines:
#            line =re.sub(r'^(input|output)\s+','',line)
#            line = re.sub(r'\b(logic|chi_flit)\b','',line)
#            line = re.sub(r'\[[^]]+\]','',line)
#            #To remove coma
#            parts = [p.strip().strip('),') for p in line.split(',')]
#            signals.extend([p for p in parts if p])
#        return signals
        
        signals = []
        for line in lines:
            # remove leading keywords
            line = re.sub(r'^(input|output)\s+', '', line)
            line = re.sub(r'\b(logic|reg|wire)\b', '', line)
            line = line.replace(";", "").replace(")", "")
            # split multiple signals declared in one line
            parts = [p.strip().strip(',') for p in line.split(',')]
            for p in parts:
                if p:
                    signals.append(p.strip())
        return signals
        
    inputs = clean_signals(raw_inputs)
    outputs = clean_signals(raw_outputs)
        
    print("Input Signals After cleaning : ",inputs)
    print("Output Signals After cleaning : ",outputs)
    
    
    #Generate Interface 
    
    it =[]
    it.append(f"interface {intf} (input logic clk);")
    for sig in inputs + outputs:
        if sig == "clk":
            continue 
        it.append(f"logic {sig};")
    it.append("endinterface")
    
   # dest_folder = "/home1/inr16/learning/scripting/Experiment/uvm_gen/"
    os.makedirs(dest_folder,exist_ok=True)
    out_file= os.path.join(dest_folder,f"{intf}.sv")
    
    with open(out_file,"w") as f:
        f.write("\n".join(it))
    
    
    #generate uvm_file (sequence_item.sv)
    
       
    seq_item_code = []
    seq_item_code.append(f"class {class_seq} extends uvm_sequence_item;")
    seq_item_code.append("")
    
    for sig in inputs:
        if sig == "clk":
            continue
        if sig == "rst":
            seq_item_code.append(f" logic {sig};")
            continue
        seq_item_code.append(f" rand logic {sig};")
    for sig in outputs:
        seq_item_code.append(f" logic {sig};")
        
    seq_item_code.append("")
    seq_item_code.append(f"`uvm_object_utils_begin ({class_seq})")
    for sig in inputs + outputs:
        if sig == "clk":
            continue
        sig_name = sig.split()[-1]
        seq_item_code.append(f"\t`uvm_field_int ({sig_name},UVM_ALL_ON)")
    seq_item_code.append("")
    seq_item_code.append(f"`uvm_object_utils_end")
    seq_item_code.append("")
    
    seq_item_code.append(f"function new ( string name = \"{class_seq}\");")
    seq_item_code.append(f"\tsuper.new(name);")
    seq_item_code.append(f"endfunction")
    
    seq_item_code.append("")
    seq_item_code.append(f"function string convert2string();")
    ports = []
    sigl =[]
    
    for sig in inputs + outputs:
        if sig == "clk":
            continue
        sig_name = sig.split()[-1]
        ports.append(f"{sig_name} = %0h ,")
        sigl.append(f"{sig_name}")
    fmt = " ".join(ports)             
    vars = ",".join(sigl)  
    #seq_item_code.append(f"\treturn $sformatf(\" {ports}\",{sigl});") 
    
    seq_item_code.append(f"\treturn $sformatf(\"{fmt}\",{vars});")
    seq_item_code.append(f"endfunction")
    
    seq_item_code.append("")
    seq_item_code.append(f"endclass")
    
    #dest_folder = "/home1/inr16/learning/scripting/Experiment/uvm_gen/"
    os.makedirs(dest_folder,exist_ok=True)
    out_file= os.path.join(dest_folder,f"{class_seq}.sv")
    
    with open(out_file,"w") as f:
        f.write("\n".join(seq_item_code))
        
    #Generate UVM File (sequencer.sv)
    
        
    seqr = []
    seqr.append(f"class {class_seqr} extends uvm_sequencer#({class_seq});")
    seqr.append("")
    
    seqr.append(f"`uvm_component_utils({class_seqr})")
    seqr.append("")
    
    seqr.append(f"function new ( string name = \"{class_seqr}\", uvm_component parent);")
    seqr.append("\tsuper.new(name,parent);")
    seqr.append("endfunction")
    seqr.append("endclass ")
    
    #out_dir = "/home1/inr16/learning/scripting/Experiment/uvm_gen/"
    os.makedirs(dest_folder,exist_ok = True)
    out_file = os.path.join(dest_folder,f"{class_seqr}.sv")
    
    with open(out_file,"w") as f:
        f.write("\n".join(seqr))
        
    
    #Generate driver 
    
    
    drv =[]
    drv.append(f"class {class_drv} extends uvm_driver#({class_seq});")
    drv.append("")
    
    drv.append(f"`uvm_component_utils({class_drv})")
    drv.append("")
    
    drv.append(f"function new (string name = \"{class_drv}\", uvm_component parent);")
    drv.append("\tsuper.new(name,parent);")
    drv.append("endfunction\n")
    
    
    drv.append(f"virtual interface {intf} vir_intf;")
    
    drv.append("function void build_phase (uvm_phase phase);")
    drv.append("\tsuper.build_phase(phase);")
    drv.append(f"if(!(uvm_config_db#( virtual {intf})::get(this,\"\",\"vir_intf\",vir_intf)))")
    drv.append("begin")
    drv.append("\t`uvm_fatal(\"DRIVER\",\"No Interface connection \");")
    drv.append("end")
    drv.append("endfunction\n")
    
    drv.append("task run_phase(uvm_phase phase);")
    drv.append(f"{class_seq} txn;")
    drv.append("forever begin")
    drv.append("\tseq_item_port.get_next_item(txn);")
    drv.append("\t@(posedge vir_intf.clk);")
    for sig in inputs :
        if sig == "clk":
            continue
        drv.append(f"\tvir_intf.{sig} = txn.{sig};")
    #drv.append("\t@(posedge vir_intf.clk);\n")
    
    drv.append("\t`uvm_info(\"DRIVER\", txn.convert2string(), UVM_LOW)")
    drv.append("\tseq_item_port.item_done();")
    drv.append("end")
    drv.append("endtask")
    drv.append("endclass")
    
   # out_dir = "/home1/inr16/learning/scripting/Experiment/uvm_gen/"
    os.makedirs(dest_folder,exist_ok = True)
    out_file = os.path.join(dest_folder,f"{class_drv}.sv")
    
    with open(out_file,"w") as f:
        f.write("\n".join(drv))
        
    #Generate Monitor
    
    
    mon = []
    mon.append(f"class {class_mon} extends uvm_monitor#({class_seq});")
  
    mon.append(f"`uvm_component_utils ({class_mon})")
  
    mon.append(f"function new ( string name =\"{class_mon}\", uvm_component parent);")
    mon.append("\tsuper.new(name,parent);")
    mon.append("endfunction")
  
    mon.append(f"virtual {intf} vir_intf;")
      
    mon.append(f"{class_seq} txn;")
    mon.append(f"uvm_analysis_port#({class_seq}) port;")
  
    mon.append("function void build_phase (uvm_phase phase);")
    mon.append("\tsuper.build_phase (phase);")
    mon.append(f"if(!(uvm_config_db#(virtual {intf})::get(this,\"\",\"vir_intf\",vir_intf)))")
    mon.append("begin")
    mon.append("\t`uvm_fatal(\"MONITOR\",\"Not Connected to Interface \");")
    mon.append("end")
    mon.append("port = new(\"port\",this);")
    mon.append(f"txn = {class_seq}::type_id::create(\"txn\",this);")
    mon.append("endfunction")

    mon.append("task run_phase (uvm_phase phase);")
    mon.append("forever begin")
    mon.append("\t@(posedge vir_intf.clk);")
    mon.append(f"\ttxn = {class_seq}::type_id::create(\"txn\", this);")
    for sig in inputs + outputs:
        if sig == "clk":
            continue
        sig_name = sig.split()[-1]
        mon.append(f"\ttxn.{sig_name} = vir_intf.{sig_name};")

        #mon.append(f"\ttxn.{sig} = vir_intf.{sig};")
        
    mon.append("\t`uvm_info(\"MONITOR\", txn.convert2string(), UVM_LOW)")
    mon.append("\tport.write(txn);")
    mon.append("end")
    mon.append("endtask")
    mon.append("endclass")
   
   # out_dir = "/home1/inr16/learning/scripting/Experiment/uvm_gen/"
    os.makedirs(dest_folder,exist_ok = True)
    out_file = os.path.join(dest_folder,f"{class_mon}.sv")
   
    with open(out_file,"w") as f:
        f.write("\n".join(mon))
       
   
    
    #Generate agent 
    
        
    agt =[]
    agt.append(f"class {class_agt} extends uvm_agent;\n")
    agt.append(f"`uvm_component_utils({class_agt})\n")
  
    agt.append(f"function new(string name=\"{class_agt}\",uvm_component parent);")
    agt.append("\tsuper.new(name,parent);")
    agt.append("endfunction")
  
    agt.append(f"{class_seqr} seqr;")
    agt.append(f"{class_drv} drv;")
    agt.append(f"{class_mon} mon;")
  
    agt.append("function void build_phase ( uvm_phase phase);")
    agt.append("\tsuper.build_phase (phase);")
    
    agt.append(f"\tseqr = {class_seqr}::type_id::create(\"seqr\",this);")
    agt.append(f"\tdrv = {class_drv}::type_id::create(\"drv\",this);")
    agt.append(f"\tmon = {class_mon}::type_id::create(\"mon\",this);")
    
    agt.append("endfunction")
  
    agt.append("function void connect_phase(uvm_phase phase);")
    agt.append("\tsuper.connect_phase(phase);")
    
    agt.append("\tdrv.seq_item_port.connect(seqr.seq_item_export);")
    agt.append("endfunction")
    agt.append("endclass")
    
    #out_dir = "/home1/inr16/learning/scripting/Experiment/uvm_gen/"
    os.makedirs(dest_folder,exist_ok=True)
    out_file = os.path.join(dest_folder,f"{class_agt}.sv")
    
    with open(out_file,"w") as f:
        f.write("\n".join(agt))
        
    #Generate scroreboard
    
    
    
    scr =[]
    scr.append(f"class {class_scr} extends uvm_scoreboard;")
    scr.append(f"`uvm_component_utils({class_scr})")
    #scr.append(f"{class_drv} ")
    scr.append(f"uvm_analysis_imp #({class_seq} , {class_scr}) analysis_export;\n")
    scr.append("function new(string name , uvm_component parent);")
    scr.append("\tsuper.new(name,parent);")
    scr.append("\tanalysis_export = new(\"analysis_export\",this);")
    scr.append("endfunction\n")
    
    for out in outputs:
        sig_name = sig.split()[-1]
        scr.append(f"logic exp_val_{sig_name};")
                
    scr.append("function void reset_model();")
    for out in outputs:
        sig_name = sig.split()[-1]
        scr.append(f"\texp_val_{sig_name} = '0;")
    scr.append("endfunction\n")
    
    scr.append(f"function void write({class_seq} txn);")
    scr.append("if(txn.rst)")
    scr.append("begin")
    scr.append("\treset_model();")
    scr.append("end else if(txn.up_dn)")
    scr.append("begin")
    for out in outputs:
        sig_name = sig.split()[-1]
        scr.append(f"\texp_val_{sig_name}++;")
    scr.append("end else begin")
    for out in outputs:
        sig_name = sig.split()[-1]
        scr.append(f"\texp_val_{sig_name}--;")
    scr.append("end\n")
    
    for out in outputs:
        sig_name = sig.split()[-1]
        scr.append(f"if(txn.{sig_name} != exp_val_{sig_name})")
        scr.append("begin")
        scr.append(f"\t`uvm_info(\"SCROREBOARD\",$sformatf(\"Mismatch on {sig_name} : Expected =%0h , Got =%0h \",exp_val_{sig_name} , txn.{sig_name}),UVM_LOW)")
        scr.append("end else begin")
        scr.append(f"\t`uvm_info(\"SCOREBOARD\", $sformatf(\"Match on {sig_name}: %0d\", txn.{sig_name}), UVM_LOW)")
    scr.append("end")
    scr.append("endfunction\n")
    scr.append("endclass")
    
   # out_dir = "/home1/inr16/learning/scripting/Experiment/uvm_gen"
    os.makedirs(dest_folder,exist_ok=True)
    out_file=os.path.join(dest_folder,f"{class_scr}.sv")
    
    with open(out_file,"w") as f:
        f.write("\n".join(scr))
        
    #Generate env.sv
    
    
    
    env =[]
    env.append(f"class {class_env} extends uvm_env;")
    env.append(f"\n`uvm_component_utils({class_env})")
    env.append(f"function new(string name = \"{class_env}\", uvm_component parent);")
    env.append("\tsuper.new(name,parent);")
    env.append("endfunction\n")
    
    env.append(f"{class_agt} agt;")
    env.append(f"{class_scr} scr;\n")
    
    env.append("function void build_phase(uvm_phase phase);")
    env.append("\tsuper.build_phase(phase);")
    env.append(f"\tagt = {class_agt}::type_id::create(\"agt\",this);")
    #env.append(f"\tscr= {class_scr}::type_id::create(\"scr\",this);")
    env.append("endfunction\n")
    
    env.append("function void connect_phase (uvm_phase phase);")
    env.append("\tsuper.connect_phase(phase);")
   # env.append("\tagt.mon.port.connect(scr.analysis_export);")
    #env.append("\tscr.connect_driver(agt.drv);")
    env.append("endfunction\n")
    env.append("endclass")
    
   # out_dir = "/home1/inr16/learning/scripting/Experiment/uvm_gen"
    os.makedirs(dest_folder,exist_ok = True)
    out_file = os.path.join(dest_folder,f"{class_env}.sv")
    
    with open(out_file,"w") as f:
        f.write("\n".join(env))
        
    #Generate Test.sv
    
    
    tst = []
    tst.append(f"class {class_tst} extends uvm_test;")
    tst.append(f"`uvm_component_utils ({class_tst})\n")
    
    tst.append(f"function new(string name =\"{class_tst}\" , uvm_component parent);")
    tst.append("\tsuper.new(name,parent);")
    tst.append("endfunction\n")
    
    tst.append(f"{class_env} env;\n")
    tst.append(f"{class_agt} agt;\n")
    
    tst.append("function void build_phase (uvm_phase phase);")
    tst.append("\tsuper.build_phase(phase);")
    tst.append(f"\tenv = {class_env}::type_id::create(\"env\",this);")
    tst.append("endfunction\n")
    
    tst.append("function void end_of_elaboration_phase(uvm_phase phase);")
    tst.append("\t$display(\"TEST\",\"End Of Elabration Phase\");")
    tst.append("endfunction\n")
    
    tst.append("function void end_of_simulation_phase(uvm_phase);")
    tst.append("$display (\"TEST\",\"End Of Simulation Phase\");")
    tst.append("set_report_severity_action_hier(UVM_INFO,UVM_DISPLAY);")
    tst.append("set_report_verbosity_level_hier(UVM_MEDIUM);")
    tst.append("endfunction\n")
  
    tst.append("task run_phase (uvm_phase phase);")
    tst.append(f"\t{class_seqn} seq;")
    tst.append("\tphase.raise_objection(this);")
    tst.append(f"\tseq = {class_seqn}::type_id::create(\"seq\",this);")
    tst.append("\tseq.start(env.agt.seqr);")
    #tst.append("\t#100;")
    tst.append("\tphase.drop_objection(this);")
    tst.append("endtask") 
    tst.append("\nendclass")
    
    #out_dir = "/home1/inr16/learning/scripting/Experiment/uvm_gen/"
    os.makedirs(dest_folder,exist_ok =True)
    out_file = os.path.join(dest_folder,f"{class_tst}.sv")
    
    with open(out_file,"w") as f:
        f.write("\n".join(tst))
        
    #Generate TB
    
    
    
    tb = []
    tb.append("`include \"uvm_macros.svh\"")
    tb.append("import uvm_pkg::*;")
    files = os.listdir("/home1/inr16/learning/scripting/Experiment/uvm_gen/")
    print(files)
    #for f in files:
     #   if f == f"{module_tb}.sv":
      #      continue
       # tb.append(f"`include \"{f}\"")
    tb.append(f"`include \"{dut_name}.sv\"")
    tb.append(f"`include \"{intf}.sv\"")
    tb.append(f"`include \"{class_seq}.sv\"")
    tb.append(f"`include \"{class_seqr}.sv\"")
    tb.append(f"`include \"{class_seqn}.sv\"")
    tb.append(f"`include \"{class_drv}.sv\"")
    tb.append(f"`include \"{class_mon}.sv\"")
    tb.append(f"`include \"{class_scr}.sv\"")
    tb.append(f"`include \"{class_agt}.sv\"")
    tb.append(f"`include \"{class_env}.sv\"")
    tb.append(f"`include \"{class_tst}.sv\"")
    tb.append(f"module {module_tb};")
    tb.append("\tlogic clk;")
    tb.append(f"{intf} intf(clk);")
    
    tb.append(f"{dut_name} dut (")
    tb.append("\t.clk(clk),")
    ports = []
    for sig in inputs + outputs:
        if sig == "clk":
            continue
        sig_name = sig.split()[-1]
        ports.append(f"\t.{sig_name}(intf.{sig_name})")
    tb.append(",\n".join(ports))
    tb.append("\t);\n")
    
    tb.append("initial begin")
    tb.append("\tclk = 0;")
    tb.append(f"\tforever #{freq} clk = ~clk;")
    tb.append("end")
    
    tb.append("initial begin")
    tb.append(f"\tintf.rst = 1;")  
    tb.append("\t#10") 
    tb.append("\trepeat (5) @(posedge clk);")
    tb.append(f"\tintf.rst = 0;")   
    tb.append("end")
    
    tb.append("initial begin ")
    tb.append(f"\tuvm_config_db#(virtual {intf})::set(uvm_root::get(),\"\",\"vir_intf\",intf);")
    tb.append("end")
    

    tb.append("initial begin")
    tb.append(f"\trun_test(\"{class_tst}\");")
    tb.append("end")
  
    tb.append("endmodule")
    
    
        
    #out_dir = "/home1/inr16/learning/scripting/Experiment/uvm_gen/"
    os.makedirs(dest_folder,exist_ok =True)
    out_file = os.path.join(dest_folder,f"{module_tb}.sv")
    
    with open(out_file,"w") as f:
        f.write("\n".join(tb))
        
    
    
    
    
    
    
    
    
        

    
    
    
    
    
    
    

           
    
    
    
    
    
        
    
    
    
    
