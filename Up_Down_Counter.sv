// Code your design here

module Up_Down_Counter (
  input logic clk , rst , up_dn ,
  output logic [7:0] data_out 
);

  
  always @(posedge clk )
    begin
      if (rst )begin
        data_out <= 0;
        $display("[%0t]RESET CLK = %b up_down_enable = %b , reset = %b , data_out =0x%02h ",$time,clk, up_dn,rst,data_out);
        end else if (up_dn )begin
          data_out <= data_out +  1; 
          $display("[%0t]FROM DUT UPCOUNT CLK = %b up_down_enable = %b , reset = %b , data_out =0x%02h ", $time,clk,up_dn,rst,data_out);
        end else begin
            data_out <= data_out - 1;
          $display("[%0t]FROM DUT DOWNCOUNT CLK =%b up_down_enable = %b , reset = %b , data_out =0x%02h ",$time, clk,up_dn,rst,data_out);
        end
        end
endmodule


      
