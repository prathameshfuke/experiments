## EXP 01 - ALU_4 pins for the Boolean Board (xc7s50csga324-1), from the faculty manual.
## Verify against the Real Digital Boolean Board master XDC if Vivado rejects a pin.
## Input a: SW0..SW3
set_property -dict { PACKAGE_PIN V2 IOSTANDARD LVCMOS33 } [get_ports {a[0]}]
set_property -dict { PACKAGE_PIN U2 IOSTANDARD LVCMOS33 } [get_ports {a[1]}]
set_property -dict { PACKAGE_PIN U1 IOSTANDARD LVCMOS33 } [get_ports {a[2]}]
set_property -dict { PACKAGE_PIN T2 IOSTANDARD LVCMOS33 } [get_ports {a[3]}]
## Input b: SW4..SW7
set_property -dict { PACKAGE_PIN T1 IOSTANDARD LVCMOS33 } [get_ports {b[0]}]
set_property -dict { PACKAGE_PIN R2 IOSTANDARD LVCMOS33 } [get_ports {b[1]}]
set_property -dict { PACKAGE_PIN R1 IOSTANDARD LVCMOS33 } [get_ports {b[2]}]
set_property -dict { PACKAGE_PIN P2 IOSTANDARD LVCMOS33 } [get_ports {b[3]}]
## Select: SW8..SW10
set_property -dict { PACKAGE_PIN P1 IOSTANDARD LVCMOS33 } [get_ports {sel[0]}]
set_property -dict { PACKAGE_PIN N2 IOSTANDARD LVCMOS33 } [get_ports {sel[1]}]
set_property -dict { PACKAGE_PIN N1 IOSTANDARD LVCMOS33 } [get_ports {sel[2]}]
## Output y: LD0..LD3
set_property -dict { PACKAGE_PIN G1 IOSTANDARD LVCMOS33 } [get_ports {y[0]}]
set_property -dict { PACKAGE_PIN G2 IOSTANDARD LVCMOS33 } [get_ports {y[1]}]
set_property -dict { PACKAGE_PIN F1 IOSTANDARD LVCMOS33 } [get_ports {y[2]}]
set_property -dict { PACKAGE_PIN F2 IOSTANDARD LVCMOS33 } [get_ports {y[3]}]
