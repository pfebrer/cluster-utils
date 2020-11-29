
describe "Host management"
	hosts_yaml=$(_clupath hosts.yaml)
	describe "Listing"
		it "Works with no hosts.yaml"
			if [ -f "${hosts_yaml}" ]; then rm "${hosts_yaml}"; fi
			assert equal "$(clu lshosts)" ""
		end

		it "Finds clusters in hosts.yaml"
			# Populate the hosts.yaml manually
			printf "cl1:\n  whatever: yes\ncl2:\n  attribute: 2\n\ncl3:" > "${hosts_yaml}"
			assert equal "$(clu lshosts)" "cl1 cl2 cl3"
			rm "${hosts_yaml}"
		end
	end

	describe "Setup and removal"
		it "Sets up clusters from multiple yaml"
			printf "cl4:\n  user: person\n  hostname: whaat\n" > "${hosts_yaml}test1"
			printf "cl5:\n  user: person\n  hostname: other\n\ncl6:\n  user: person\n  hostname: hpc" > "${hosts_yaml}test2"
			clu setuphost --config ${hosts_yaml}test? --use-defaults --no-conn #>/dev/null 2>/dev/null
			rm ${hosts_yaml}test?
			assert equal "$(clu lshosts)" "cl4 cl5 cl6"
		end

		it "Removes one cluster succesfully"
			clu removehost cl5
			assert equal "$(clu lshosts)" "cl4 cl6"
		end

		it "Removes all clusters succesfully"
			clu removehost --all
			assert equal "$(clu lshosts)" ""
		end
	end
	
end
